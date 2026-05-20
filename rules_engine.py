# rules_engine.py

def arabize_features(feat):
    """حقائق ثابتة لترجمة الميزات الصرفية بدون استخدام شروط"""
    genders = {'m': "مذكر", 'f': "مؤنث"}
    numbers = {'s': "مفرد", 'd': "مثنى", 'p': "جمع"}
    persons = {'1': "متكلم", '2': "مخاطب", '3': "غائب"}
    voices = {'a': "مبني للمعلوم", 'p': "مبني للمجهول"}

    return {
        "gender": genders.get(feat['gen'], ""),
        "number": numbers.get(feat['num'], ""),
        "person": persons.get(feat['per'], ""),
        "voice": voices.get(feat['vox'], "")
    }


def iearab_verb(feat, forced_type=None):
    """محرك القواعد للأفعال باستخدام match/case البديل النظيف لـ if"""
    features_ar = arabize_features(feat)
    voice_str = f" ({features_ar['voice']})"

    match (forced_type, feat['aspect'], feat['mode'], feat['per']):
        # حالة مجبرة سياقياً: فعل ماضٍ اتصلت به تاء الفاعل (أكلتُ)
        case ('tu_ta', _, _, _) | (None, 'p', _, '1') | (None, 'p', _, '2'):
            irab_string = f"فعل ماضٍ مبني على السكون لاتصاله بتاء الفاعل{voice_str}، والتاء ضمير متصل في محل رفع فاعل"
            diac = feat['word'][:-1] + 'ْتُ'
        # ماضي عادي أو تاء تأنيث ساكنة (أكلتْ الهندُ)
        case (None, 'p', _, '3'):
            irab_string = f"فعل ماضٍ مبني على الفتح{voice_str}"
            diac = feat['diac']
        # المضارع المرفوع
        case (None, 'i', 'u', _):
            irab_string = f"فعل مضارع مرفوع وعلامة رفعه الضمة الظاهرة{voice_str}"
            diac = feat['diac']
        # المضارع المنصوب
        case (None, 'i', 'a', _):
            irab_string = f"فعل مضارع منصوب وعلامة نصبه الفتحة الظاهرة{voice_str}"
            diac = feat['diac']
        # المضارع المجزوم
        case (None, 'i', 'j', _):
            irab_string = f"فعل مضارع مجزوم وعلامة جزمه السكون{voice_str}"
            diac = feat['diac']
        # فعل الأمر
        case (None, 'c', _, _):
            irab_string = "فعل أمر مبني على السكون، والفاعل ضمير مستتر تقديره أنت"
            diac = feat['diac']
        case _:
            irab_string = "فعل (لم يتم تصنيفه)"
            diac = feat['diac']

    return {"word": feat['word'], "diac": diac, "irab": irab_string}


def fix_imperative_rule(feat):
    """قاعدة تصحيح فعل الأمر: تعديل الحقيقة الصرفية إذا بدأت الكلمة بألف وجاءت بصيغة المتكلم خطأً"""
    word_text = feat['word']

    match word_text[0]:
        case 'ا' | 'أ':
            is_alif = True
        case _:
            is_alif = False

    match (feat['pos'], feat['aspect'], feat['per'], is_alif):
        case ('verb', 'i', '1', True):
            feat['aspect'] = 'c'
            feat['diac'] = 'اِ' + word_text[1:] + 'ْ'
        case _:
            pass

    return feat


def check_context_ambiguity(analyzed_features):
    """قاعدة نحوية ذكية لتحديد تاء الفاعل بناءً على طبيعة الاسم التالي (عاقل/جماد)"""
    non_human_objects = ["التفاحة", "تفاحة", "الخبز", "خبز", "الدرس", "درس", "الماء", "ماء", "الكتاب", "كتاب"]

    match (len(analyzed_features) >= 2):
        case True:
            word1 = analyzed_features[0]['word']
            word2 = analyzed_features[1]['word']

            match (analyzed_features[0]['pos'] == 'verb', word1.endswith('ت'), word2 in non_human_objects):
                case (True, True, True):
                    return 'tu_ta'
                case _:
                    return None
        case _:
            return None


# =====================================================================
#  حزمة قواعد الإعراب المنفصلة (تسهل عليك إضافة أي حقيقة نحوية مستقبلاً)
# =====================================================================
def handle_noun_rules(state, feat):
    """قواعد إعراب الأسماء والصفات وأسماء العلم بناءً على حالة السياق وفحص الحروف المتصلة"""
    word_text = feat['word']

    # 1. قاعدة الاسم المجرور بحرف جر منفصل سابق (مثل: في المدرسةِ)
    match state['is_majroor']:
        case True:
            state['is_majroor'] = False  # تصفير المؤشر فور الاستهلاك
            return "اسم مجرور وعلامة جره الكسرة الظاهرة"

    # 2. قاعدة حروف الجر المتصلة الذكية والديناميكية (بـ، كـ، لـ)
    match (word_text[0], word_text.startswith('ال')):
        # إذا بدأت بالباء أو الكاف وتتصل بـ ال التعريف (مثل: بالكرة، كالكرة)
        case ('ب', False) if word_text[1:].startswith('ال'):
            return f"حرف جر (الباء)، و{word_text[1:]}: اسم مجرور وعلامة جره الكسرة الظاهرة"
        case ('ك', False) if word_text[1:].startswith('ال'):
            return f"حرف جر (الكاف)، و{word_text[1:]}: اسم مجرور وعلامة جره الكسرة الظاهرة"

        # إذا بدأت بـ لـ الجر المتصلة بالتعريف (مثل: للمدرسة -> تحذف الألف وتصبح لـ + المدرسة)
        case ('ل', False) if word_text[1:].startswith('ل'):
            return f"حرف جر (اللام)، والم{word_text[2:]}: اسم مجرور وعلامة جره الكسرة الظاهرة"

        # حالات الاتصال بأسماء نكرة (مثل: بكرةٍ، كأَسدٍ، لولدٍ)
        case ('ب', False) if feat['pos'] in ['noun', 'adj', 'noun_prop'] and len(word_text) > 2:
            return f"حرف جر (الباء)، و{word_text[1:]}: اسم مجرور وعلامة جره الكسرة"
        case ('ك', False) if feat['pos'] in ['noun', 'adj', 'noun_prop'] and len(word_text) > 2:
            return f"حرف جر (الكاف)، و{word_text[1:]}: اسم مجرور وعلامة جره الكسرة"
        case ('ل', False) if feat['pos'] in ['noun', 'adj', 'noun_prop'] and len(word_text) > 2:
            return f"حرف جر (اللام)، و{word_text[1:]}: اسم مجرور وعلامة جره الكسرة"

    # 3. قواعد الفاعل والمفعول الافتراضية للأسماء وأسماء العلم
    match (state['has_subject'], feat['cas']):
        case (True, _):
            return "مفعول به منصوب وعلامة نصبه الفتحة الظاهرة"
        case (False, 'u') | (False, 'na'):
            state['has_subject'] = True
            return "فاعل مرفوع وعلامة رفعه الضمة الظاهرة"
        case _:
            return "مفعول به منصوب وعلامة نصبه الفتحة الظاهرة"
def handle_pronoun_rules(state, feat):
    """قواعد إعراب الضمائر المتصلة والمنفصلة سياقياً"""
    match state['is_majroor']:
        case True:
            state['is_majroor'] = False
            return "ضمير متصل مبني في محل جر بحرف الجر"

    match feat['cas']:
        case 'u':
            state['has_subject'] = True
            return "ضمير متصل مبني في محل رفع فاعل"
        case 'a':
            return "ضمير متصل مبني في محل نصب مفعول به"
        case _:
            return f"ضمير (موقعه الإعرابي: {feat['cas']})"


# =====================================================================
#  المحرك الرئيسي لمعالجة المدخلات وتوجيهها
# =====================================================================
def process_word_rule(state, feat):
    """الموجه الرئيسي للكلمات - يدعم الآن noun_prop (أسماء العلم) بشكل فليكسيبل"""
    feat = fix_imperative_rule(feat)
    pos = feat['pos']
    per = feat['per']

    match pos:
        case 'verb':
            state['is_majroor'] = False
            match (state['forced_verb_context'], feat['aspect'], per):
                case ('tu_ta', _, _) | (None, 'p', '1') | (None, 'p', '2'):
                    state['has_subject'] = True
                case _:
                    state['has_subject'] = False
            result = iearab_verb(feat, forced_type=state['forced_verb_context'])

        case 'prep':
            state['is_majroor'] = True
            result = {"word": feat['word'], "diac": feat['diac'], "irab": "حرف جر"}

        # إضافة دعم noun_prop (مثل: سليم، محمد) ليتم توجيهها لقواعد الأسماء والفاعل
        case 'noun' | 'adj' | 'noun_prop':
            irab_str = handle_noun_rules(state, feat)
            result = {"word": feat['word'], "diac": feat['diac'], "irab": irab_str}

        case 'pron':
            irab_str = handle_pronoun_rules(state, feat)
            result = {"word": feat['word'], "diac": feat['diac'], "irab": irab_str}

        case _:
            state['is_majroor'] = False
            result = {"word": feat['word'], "diac": feat['diac'], "irab": f"نوع الكلمة النحوي: {pos}"}

    state['outputs'].append(result)
    return state
def apply_irab_to_sentence(analyzed_features):
    """المحرك الرئيسي لتوليد الإعراب بدون استخدام لولب تكراري (for)"""
    context_decision = check_context_ambiguity(analyzed_features)

    # الـ State مجهز ومفتوح لإضافة أي متتبع جديد مستقبلاً (مثل: 'in_kan_khabar')
    state = {
        'has_subject': False,
        'forced_verb_context': context_decision,
        'is_majroor': False,  # المتتبع الجديد الخاص بالجار والمجرور
        'outputs': []
    }

    # معالجة القائمة عبر القواعد بأسلوب الـ List Comprehension النظيف
    [process_word_rule(state, feat) for feat in analyzed_features]

    return state['outputs']