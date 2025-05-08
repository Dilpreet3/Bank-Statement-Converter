# 🏦 Bank Statement Converter - SaaS Tool

A **fully working SaaS tool** to convert bank statement PDFs into Excel or CSV format — built in **Flask + Python**, matching the functionality of [https://bankstatementconverter.com ](https://bankstatementconverter.com ).

## 🔍 Features

| Feature | Description |
|--------|-------------|
| 📤 Drag-and-drop upload | Supports standard & scanned PDFs |
| 🧠 Automatic PDF-to-Excel conversion | Using `pdfplumber` |
| ⚠️ Fallback to manual mode (`/inspect`) | Canvas-based grid drawing |
| 💰 Stripe Integration | One-time or subscription payments |
| 📨 Email Delivery | Uses SendGrid |
| 👤 User Auth System | Login/Register/Dashboard |
| 📋 Pricing Tiers | Anonymous / Registered / Subscribe |
| 📁 File History | View past conversions |
| 🧩 Responsive Design | Mobile/tablet/desktop friendly |
| 🌐 RESTful API | `/upload`, `/status`, `/convert`, `/set-password`, `/user` |
| 🧬 Password-Protected PDF Support | Basic support via PyMuPDF |

---

## 🧾 Technologies Used

- **Backend**: Flask + SQLAlchemy
- **Frontend**: HTML/CSS + JavaScript
- **PDF Parsing**: pdfplumber + PyMuPDF
- **OCR**: pytesseract + OpenCV
- **Email**: SendGrid
- **Payments**: Stripe Checkout
- **Styling**: Bootstrap 5 + CSS variables (matching original site)

---

## 📦 How to Run Locally

### 1. Clone the repo:

```bash
git clone https://github.com/yourusername/bank-statement-converter.git 
cd bank-statement-converter
