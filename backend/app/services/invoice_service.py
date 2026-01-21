"""Enhanced Invoice Service with Catalogue Integration, PDF Generation, and Email"""
import uuid
import os
import io
import base64
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from pydantic import BaseModel
from app.core.database import get_db

# Intelligence Graph logging
from app.services.intelligence_service import log_invoice_event, log_brand_event

# PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.units import mm, inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# SendGrid for email
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
    SENDGRID_KEY = os.environ.get("SENDGRID_API_KEY")
    SENDGRID_FROM = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@enterprate.ai")
    SENDGRID_AVAILABLE = bool(SENDGRID_KEY)
except ImportError:
    SENDGRID_AVAILABLE = False
    SENDGRID_KEY = None
    SENDGRID_FROM = None


class LineItem(BaseModel):
    catalogueItemId: Optional[str] = None
    name: str
    description: Optional[str] = None
    quantity: float = 1
    unitPrice: float
    taxRate: Optional[float] = None


class EnhancedInvoiceCreate(BaseModel):
    clientName: str
    clientEmail: str
    clientAddress: Optional[str] = None
    lineItems: List[LineItem]
    currency: str = "GBP"
    dueDate: Optional[str] = None
    notes: Optional[str] = None
    termsAndConditions: Optional[str] = None
    status: str = "draft"  # draft, pending_review, sent, paid, overdue


class InvoiceUpdateStatus(BaseModel):
    status: str


class BrandAssetCreate(BaseModel):
    assetType: str = "logo"  # logo, letterhead, etc.
    imageBase64: str
    filename: str


class InvoiceService:
    """Enhanced Invoice Service"""
    
    @staticmethod
    async def create_invoice(workspace_id: str, user_id: str, data: EnhancedInvoiceCreate) -> dict:
        """Create a new invoice with line items"""
        db = get_db()
        
        # Generate invoice number
        count = await db.invoices.count_documents({"workspace_id": workspace_id})
        invoice_number = f"INV-{datetime.now().strftime('%Y%m')}-{count + 1:04d}"
        
        # Calculate totals
        subtotal = 0
        tax_total = 0
        line_items_data = []
        
        for item in data.lineItems:
            item_subtotal = item.quantity * item.unitPrice
            item_tax = item_subtotal * (item.taxRate / 100) if item.taxRate else 0
            
            line_items_data.append({
                "catalogueItemId": item.catalogueItemId,
                "name": item.name,
                "description": item.description,
                "quantity": item.quantity,
                "unitPrice": item.unitPrice,
                "taxRate": item.taxRate,
                "subtotal": round(item_subtotal, 2),
                "taxAmount": round(item_tax, 2),
                "total": round(item_subtotal + item_tax, 2)
            })
            
            subtotal += item_subtotal
            tax_total += item_tax
        
        total = subtotal + tax_total
        
        invoice_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        invoice = {
            "id": invoice_id,
            "workspace_id": workspace_id,
            "invoiceNumber": invoice_number,
            "clientName": data.clientName,
            "clientEmail": data.clientEmail,
            "clientAddress": data.clientAddress,
            "lineItems": line_items_data,
            "currency": data.currency,
            "subtotal": round(subtotal, 2),
            "taxTotal": round(tax_total, 2),
            "total": round(total, 2),
            "dueDate": data.dueDate,
            "notes": data.notes,
            "termsAndConditions": data.termsAndConditions,
            "status": data.status,
            "invoiceDate": now[:10],
            "created_by": user_id,
            "createdAt": now,
            "updatedAt": now
        }
        
        await db.invoices.insert_one(invoice)
        
        # Log event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "invoice_created",
            "data": {
                "invoice_id": invoice_id,
                "invoiceNumber": invoice_number,
                "total": total,
                "status": data.status
            },
            "occurredAt": now
        })
        
        return {k: v for k, v in invoice.items() if k != '_id'}
    
    @staticmethod
    async def get_invoices(workspace_id: str, status: Optional[str] = None) -> List[dict]:
        """Get all invoices for workspace"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if status:
            query["status"] = status
        
        invoices = await db.invoices.find(query).sort("createdAt", -1).to_list(length=500)
        return [{k: v for k, v in inv.items() if k != '_id'} for inv in invoices]
    
    @staticmethod
    async def get_invoice(invoice_id: str, workspace_id: str) -> dict:
        """Get single invoice"""
        db = get_db()
        
        invoice = await db.invoices.find_one({
            "id": invoice_id,
            "workspace_id": workspace_id
        })
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {k: v for k, v in invoice.items() if k != '_id'}
    
    @staticmethod
    async def update_invoice(invoice_id: str, workspace_id: str, data: dict) -> dict:
        """Update invoice"""
        db = get_db()
        
        invoice = await db.invoices.find_one({
            "id": invoice_id,
            "workspace_id": workspace_id
        })
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Don't allow editing sent/paid invoices
        if invoice.get("status") in ["sent", "paid"] and data.get("status") not in ["sent", "paid", "overdue"]:
            raise HTTPException(status_code=400, detail="Cannot edit sent or paid invoices")
        
        data["updatedAt"] = datetime.now(timezone.utc).isoformat()
        
        await db.invoices.update_one(
            {"id": invoice_id, "workspace_id": workspace_id},
            {"$set": data}
        )
        
        updated = await db.invoices.find_one({"id": invoice_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def finalize_invoice(invoice_id: str, workspace_id: str) -> dict:
        """Finalize invoice (move from draft to pending_review)"""
        db = get_db()
        
        invoice = await db.invoices.find_one({
            "id": invoice_id,
            "workspace_id": workspace_id
        })
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        if invoice.get("status") != "draft":
            raise HTTPException(status_code=400, detail="Only draft invoices can be finalized")
        
        await db.invoices.update_one(
            {"id": invoice_id},
            {"$set": {"status": "pending_review", "updatedAt": datetime.now(timezone.utc).isoformat()}}
        )
        
        updated = await db.invoices.find_one({"id": invoice_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def generate_pdf(invoice_id: str, workspace_id: str) -> bytes:
        """Generate PDF for invoice"""
        if not PDF_AVAILABLE:
            raise HTTPException(status_code=500, detail="PDF generation not available")
        
        db = get_db()
        
        invoice = await db.invoices.find_one({
            "id": invoice_id,
            "workspace_id": workspace_id
        })
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Get workspace info for company details
        workspace = await db.workspaces.find_one({"id": workspace_id})
        company_name = workspace.get("name", "Your Company") if workspace else "Your Company"
        
        # Get brand logo if available
        brand_asset = await db.brand_assets.find_one({
            "workspace_id": workspace_id,
            "assetType": "logo"
        })
        
        # Generate PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            textColor=colors.HexColor('#4F46E5')
        )
        
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey
        )
        
        # Logo and Header
        header_data = []
        if brand_asset and brand_asset.get("imageData"):
            try:
                logo_data = base64.b64decode(brand_asset["imageData"])
                logo_buffer = io.BytesIO(logo_data)
                logo = Image(logo_buffer, width=60*mm, height=20*mm)
                header_data.append([logo, Paragraph(f"<b>{company_name}</b>", styles['Normal'])])
            except Exception:
                header_data.append([Paragraph(f"<b>{company_name}</b>", title_style)])
        else:
            header_data.append([Paragraph(f"<b>{company_name}</b>", title_style)])
        
        # Invoice title
        elements.append(Paragraph("INVOICE", title_style))
        elements.append(Spacer(1, 10*mm))
        
        # Invoice details
        invoice_info = [
            ["Invoice Number:", invoice.get("invoiceNumber", "N/A")],
            ["Invoice Date:", invoice.get("invoiceDate", "N/A")],
            ["Due Date:", invoice.get("dueDate", "N/A")],
            ["Status:", invoice.get("status", "draft").upper()]
        ]
        
        info_table = Table(invoice_info, colWidths=[100, 200])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 10*mm))
        
        # Bill To
        elements.append(Paragraph("<b>Bill To:</b>", styles['Normal']))
        elements.append(Paragraph(invoice.get("clientName", ""), styles['Normal']))
        elements.append(Paragraph(invoice.get("clientEmail", ""), header_style))
        if invoice.get("clientAddress"):
            elements.append(Paragraph(invoice.get("clientAddress"), header_style))
        elements.append(Spacer(1, 10*mm))
        
        # Line items table
        currency_symbol = "£" if invoice.get("currency") == "GBP" else "$" if invoice.get("currency") == "USD" else "€"
        
        line_items = invoice.get("lineItems", [])
        table_data = [["Description", "Qty", "Unit Price", "Tax", "Total"]]
        
        for item in line_items:
            table_data.append([
                item.get("name", ""),
                str(item.get("quantity", 1)),
                f"{currency_symbol}{item.get('unitPrice', 0):.2f}",
                f"{item.get('taxRate', 0) or 0}%",
                f"{currency_symbol}{item.get('total', 0):.2f}"
            ])
        
        items_table = Table(table_data, colWidths=[220, 50, 80, 50, 80])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 5*mm))
        
        # Totals
        totals_data = [
            ["Subtotal:", f"{currency_symbol}{invoice.get('subtotal', 0):.2f}"],
            ["Tax:", f"{currency_symbol}{invoice.get('taxTotal', 0):.2f}"],
            ["Total:", f"{currency_symbol}{invoice.get('total', 0):.2f}"],
        ]
        
        totals_table = Table(totals_data, colWidths=[380, 100])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ]))
        elements.append(totals_table)
        
        # Notes
        if invoice.get("notes"):
            elements.append(Spacer(1, 10*mm))
            elements.append(Paragraph("<b>Notes:</b>", styles['Normal']))
            elements.append(Paragraph(invoice.get("notes"), header_style))
        
        # Terms
        if invoice.get("termsAndConditions"):
            elements.append(Spacer(1, 10*mm))
            elements.append(Paragraph("<b>Terms & Conditions:</b>", styles['Normal']))
            elements.append(Paragraph(invoice.get("termsAndConditions"), header_style))
        
        # Build PDF
        doc.build(elements)
        
        return buffer.getvalue()
    
    @staticmethod
    async def send_invoice_email(invoice_id: str, workspace_id: str, user_id: str) -> dict:
        """Send invoice via email"""
        if not SENDGRID_AVAILABLE:
            raise HTTPException(status_code=500, detail="Email service not configured")
        
        db = get_db()
        
        invoice = await db.invoices.find_one({
            "id": invoice_id,
            "workspace_id": workspace_id
        })
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Generate PDF
        pdf_content = await InvoiceService.generate_pdf(invoice_id, workspace_id)
        
        # Get workspace info
        workspace = await db.workspaces.find_one({"id": workspace_id})
        company_name = workspace.get("name", "Your Company") if workspace else "Your Company"
        
        # Prepare email
        currency_symbol = "£" if invoice.get("currency") == "GBP" else "$" if invoice.get("currency") == "USD" else "€"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #4F46E5;">Invoice from {company_name}</h2>
            
            <p>Dear {invoice.get('clientName')},</p>
            
            <p>Please find attached your invoice <strong>{invoice.get('invoiceNumber')}</strong>.</p>
            
            <table style="margin: 20px 0; border-collapse: collapse;">
                <tr>
                    <td style="padding: 5px 20px 5px 0; font-weight: bold;">Invoice Number:</td>
                    <td>{invoice.get('invoiceNumber')}</td>
                </tr>
                <tr>
                    <td style="padding: 5px 20px 5px 0; font-weight: bold;">Amount Due:</td>
                    <td style="font-size: 18px; color: #4F46E5;">{currency_symbol}{invoice.get('total', 0):.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 5px 20px 5px 0; font-weight: bold;">Due Date:</td>
                    <td>{invoice.get('dueDate', 'Upon receipt')}</td>
                </tr>
            </table>
            
            <p>If you have any questions, please don't hesitate to contact us.</p>
            
            <p>Thank you for your business!</p>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                Best regards,<br>
                {company_name}
            </p>
        </body>
        </html>
        """
        
        message = Mail(
            from_email=SENDGRID_FROM,
            to_emails=invoice.get("clientEmail"),
            subject=f"Invoice {invoice.get('invoiceNumber')} from {company_name}",
            html_content=html_content
        )
        
        # Attach PDF
        encoded_pdf = base64.b64encode(pdf_content).decode()
        attachment = Attachment(
            FileContent(encoded_pdf),
            FileName(f"{invoice.get('invoiceNumber')}.pdf"),
            FileType("application/pdf"),
            Disposition("attachment")
        )
        message.attachment = attachment
        
        try:
            sg = SendGridAPIClient(SENDGRID_KEY)
            response = sg.send(message)
            
            if response.status_code in [200, 202]:
                # Update invoice status to sent
                await db.invoices.update_one(
                    {"id": invoice_id},
                    {"$set": {
                        "status": "sent",
                        "sentAt": datetime.now(timezone.utc).isoformat(),
                        "updatedAt": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                # Log event
                await db.intelligence_events.insert_one({
                    "id": str(uuid.uuid4()),
                    "workspace_id": workspace_id,
                    "type": "invoice_sent",
                    "data": {
                        "invoice_id": invoice_id,
                        "invoiceNumber": invoice.get("invoiceNumber"),
                        "recipient": invoice.get("clientEmail")
                    },
                    "occurredAt": datetime.now(timezone.utc).isoformat()
                })
                
                return {"success": True, "message": "Invoice sent successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to send email")
                
        except Exception as e:
            print(f"SendGrid error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    
    # === Brand Assets ===
    
    @staticmethod
    async def save_brand_asset(workspace_id: str, user_id: str, data: BrandAssetCreate) -> dict:
        """Save or update a brand asset (logo)"""
        db = get_db()
        
        asset_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        # Check if asset type already exists
        existing = await db.brand_assets.find_one({
            "workspace_id": workspace_id,
            "assetType": data.assetType
        })
        
        asset_data = {
            "workspace_id": workspace_id,
            "assetType": data.assetType,
            "filename": data.filename,
            "imageData": data.imageBase64,
            "updated_by": user_id,
            "updatedAt": now
        }
        
        if existing:
            # Update existing
            await db.brand_assets.update_one(
                {"id": existing["id"]},
                {"$set": asset_data}
            )
            asset_id = existing["id"]
        else:
            # Create new
            asset_data["id"] = asset_id
            asset_data["created_by"] = user_id
            asset_data["createdAt"] = now
            await db.brand_assets.insert_one(asset_data)
        
        # Log event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "brand_asset_saved",
            "data": {"assetType": data.assetType, "filename": data.filename},
            "occurredAt": now
        })
        
        return {"id": asset_id, "success": True, "assetType": data.assetType}
    
    @staticmethod
    async def get_brand_assets(workspace_id: str) -> List[dict]:
        """Get all brand assets for workspace"""
        db = get_db()
        
        assets = await db.brand_assets.find({"workspace_id": workspace_id}).to_list(length=50)
        
        # Don't return full image data in list - just metadata
        return [{
            "id": a.get("id"),
            "assetType": a.get("assetType"),
            "filename": a.get("filename"),
            "updatedAt": a.get("updatedAt")
        } for a in assets]
    
    @staticmethod
    async def get_brand_asset(workspace_id: str, asset_type: str) -> Optional[dict]:
        """Get a specific brand asset"""
        db = get_db()
        
        asset = await db.brand_assets.find_one({
            "workspace_id": workspace_id,
            "assetType": asset_type
        })
        
        if not asset:
            return None
        
        return {
            "id": asset.get("id"),
            "assetType": asset.get("assetType"),
            "filename": asset.get("filename"),
            "imageData": asset.get("imageData"),
            "updatedAt": asset.get("updatedAt")
        }
    
    @staticmethod
    async def delete_brand_asset(workspace_id: str, asset_type: str) -> dict:
        """Delete a brand asset"""
        db = get_db()
        
        result = await db.brand_assets.delete_one({
            "workspace_id": workspace_id,
            "assetType": asset_type
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Brand asset not found")
        
        return {"success": True, "message": "Brand asset deleted"}
