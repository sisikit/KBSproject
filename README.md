# 🚀 Arabic Parsing API

مشروع برمجي متكامل لاستخراج السمات الصرفية والنحوية للنصوص العربية باستخدام **CAMeL Tools** و **FastAPI**.

---

## 🛠 المتطلبات (Prerequisites)
قبل البدء، تأكدي من تثبيت:
* **Python 3.10+**
* **Git**

---

## ⚙️ خطوات التشغيل

### 1. إعداد البيئة الافتراضية
افتحي الـ Terminal في مجلد المشروع ونفذي الأوامر التالية:

```bash
# إنشاء البيئة
python -m venv venv

# تفعيل البيئة (على ويندوز)
.\venv\Scripts\activate
pip install camel-tools fastapi uvicorn
camel_data -i morphology-db-msa-r13
camel_data -i disambig-mle-calima-msa-r13
# تشغيل السيرفر 
uvicorn main:app --reload
http://127.0.0.1:8000/docs