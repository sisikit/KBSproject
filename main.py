# main.py
import sys
from nlp_processor import process_sentence_for_i3rab


def print_result(res):
    """طباعة مبسطة تعرض الكلمة بتشكيلها وإعرابها النحوي فقط"""
    print(f"الكلمة: {res['word']} [{res['diac']}]")
    print(f"  الإعراب: {res['irab']}")
    print("-" * 30)


def start_engine():
    print("\n--- مرحباً بك في محرك الإعراب الصرفي للأفعال ---")
    print("اكتب 'خروج' أو 'exit' لإنهاء البرنامج.\n")

    while True:
        user_input = input("أدخل الجملة العربية المراد تحليلها: ").strip()

        match user_input.lower():
            case 'exit' | 'خروج' | '':
                print("شكراً لاستخدامك المحرك!")
                break
            case _:
                try:
                    analysis_results = process_sentence_for_i3rab(user_input)

                    print("\n" + "=" * 50)
                    print(f"تحليل جملة: '{user_input}'")
                    print("=" * 50)

                    [print_result(res) for res in analysis_results]

                except Exception as e:
                    print(f"حدث خطأ أثناء المعالجة: {e}")


match __name__:
    case "__main__":
        start_engine()