import re
from camel_tools.utils.dediac import dediac_ar
from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.disambig.mle import MLEDisambiguator

mle = MLEDisambiguator.pretrained('calima-msa-r13')

def clean_text(raw_input):
    text = re.sub(r'\s+', ' ', raw_input).strip()
    return dediac_ar(text)

def process_sentence_for_i3rab(raw_sentence):
    cleaned = clean_text(raw_sentence)
    tokens = simple_word_tokenize(cleaned)
    disambiguated = mle.disambiguate(tokens)
    
    final_features = []
    for word_obj in disambiguated:
        best = word_obj.analyses[0].analysis
        final_features.append({

            # الكلمة الأصلية من النص
            'word': word_obj.word,

            # الكلمة بعد التشكيل
            # مثال: "نرغب" → "نَرْغَب"
            'diac': best.get('diac', 'na'),

            # نوع الكلمة (Part Of Speech)
            # أهم الاحتمالات:
            # noun  = اسم
            # verb  = فعل
            # adj   = صفة
            # adv   = ظرف
            # prep  = حرف جر
            # conj  = حرف عطف
            # part  = أداة/حرف
            # pron  = ضمير
            'pos': best.get('pos', 'na'),

            # الحالة الإعرابية للأسماء غالباً
            # u = مرفوع
            # a = منصوب
            # g = مجرور
            # na = لا ينطبق (غالباً للأفعال أو الحروف)
            'cas': best.get('cas', 'na'),

            # الجذر الصرفي
            # مثال:
            # "نرغب" → "ر.غ.ب"
            'root': best.get('root', 'na'),

            # الوزن الصرفي
            # الأرقام تمثل حروف الجذر:
            # 1 = فاء الكلمة
            # 2 = عين الكلمة
            # 3 = لام الكلمة
            #
            # مثال:
            # "نَ1ْ2َ3" → نَرْغَب
            'pattern': best.get('pattern', 'na'),

            # aspect / asp = نوع أو زمن الفعل
            #
            # p = فعل ماضٍ
            # i = فعل مضارع
            # c = فعل أمر
            # na = لا ينطبق
            'aspect': best.get('asp', 'na'),

            # mode / mod = الحالة الإعرابية للفعل المضارع
            #
            # u = مرفوع
            # a = منصوب
            # j = مجزوم
            # na = لا ينطبق
            #
            # مثال:
            # "نرغب" → u
            'mode': best.get('mod', 'na'),

            # الشخص (Person)
            #
            # 1 = متكلم
            # 2 = مخاطب
            # 3 = غائب
            'per': best.get('per', 'na'),

            # الجنس (Gender)
            #
            # m = مذكر
            # f = مؤنث
            # na = لا ينطبق
            'gen': best.get('gen', 'na'),

            # العدد (Number)
            #
            # s = مفرد
            # d = مثنى
            # p = جمع
            # na = لا ينطبق
            'num': best.get('num', 'na'),

            # المبني للمعلوم أو المجهول (Voice)
            #
            # a = مبني للمعلوم
            # p = مبني للمجهول
            # na = لا ينطبق
            'vox': best.get('vox', 'na'),

        })
    return final_features