# 需要安装: pip install lingua-language-detector
import re

try:
    from lingua import Language, LanguageDetectorBuilder
    lingua_AVAILABLE = True
except ImportError:
    lingua_AVAILABLE = False
    print("lingua库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "lingua-language-detector"])
        print("lingua库安装成功，正在导入...")
        from lingua import Language, LanguageDetectorBuilder
        lingua_AVAILABLE = True
        print("✅ lingua库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install lingua-language-detector")
        lingua_AVAILABLE = False

# 创建语言检测器
if lingua_AVAILABLE:
    languages = [
        Language.CHINESE, Language.JAPANESE, Language.KOREAN, 
        Language.ARABIC, Language.RUSSIAN, Language.ENGLISH,
        Language.SPANISH, Language.FRENCH, Language.ITALIAN, 
        Language.PORTUGUESE, Language.GERMAN
    ]
    detector = LanguageDetectorBuilder.from_languages(*languages).build()

def detect_primary_language(text):
    """
    检测文本的主要语言，支持11种语言
    使用 lingua 库进行更准确的语言检测
    如果主要语言是中文或阿拉伯语，则返回第一个非中文非阿拉伯语的语言
    """
    # 如果文本太短或为空，使用字符特征检测
    if not text or len(text.strip()) < 10:
        result = detect_by_character_features(text)
        if result in ['zh', 'ar']:
            # 对于短文本，如果是中文或阿拉伯语，返回英语作为默认
            return 'en'
        return result
    
    if not lingua_AVAILABLE:
        result = detect_by_character_features(text)
        if result in ['zh', 'ar']:
            return 'en'
        return result
    
    try:
        # 使用 lingua 获取语言置信度排序
        confidence_values = detector.compute_language_confidence_values(text)
        
        if not confidence_values:
            result = detect_by_character_features(text)
            if result in ['zh', 'ar']:
                return 'en'
            return result
        
        # 映射到我们支持的语言代码
        lang_mapping = {
            Language.CHINESE: 'zh',
            Language.JAPANESE: 'ja',
            Language.KOREAN: 'ko',
            Language.ARABIC: 'ar',
            Language.RUSSIAN: 'ru',
            Language.ENGLISH: 'en',
            Language.SPANISH: 'es',
            Language.FRENCH: 'fr',
            Language.ITALIAN: 'it',
            Language.PORTUGUESE: 'pt',
            Language.GERMAN: 'de'
        }
        
        # 获取排序后的语言列表
        sorted_languages = []
        for confidence in confidence_values:
            lang_code = lang_mapping.get(confidence.language)
            if lang_code:
                sorted_languages.append((lang_code, confidence.value))
        
        if not sorted_languages:
            return 'en'
        
        # 寻找第一个非中文非阿拉伯语的语言
        for lang_code, confidence in sorted_languages:
            if lang_code not in ['zh', 'ar']:
                return lang_code
        
        # 如果所有检测到的语言都是中文或阿拉伯语，返回英语作为默认
        return 'en'
        
    except Exception:
        # 如果检测失败，回退到字符特征检测
        result = detect_by_character_features(text)
        if result in ['zh', 'ar']:
            return 'en'
        return result

def detect_by_character_features(text):
    """
    基于字符特征的语言检测（作为 lingua 的备用方案）
    """
    if not text:
        return 'en'
    
    # 中文字符 (Chinese)
    if re.search(r'[\u4e00-\u9fff]', text):
        return 'zh'
    # 日文字符 (Japanese)
    elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
        return 'ja'
    # 韩文字符 (Korean)
    elif re.search(r'[\uac00-\ud7af]', text):
        return 'ko'
    # 阿拉伯文字符 (Arabic)
    elif re.search(r'[\u0600-\u06ff]', text):
        return 'ar'
    # 俄文字符 (Russian)
    elif re.search(r'[\u0400-\u04ff]', text):
        return 'ru'
    # 默认英语
    else:
        return 'en'

def detect_romance_language(text):
    """
    检测罗曼语族语言 (西班牙语、法语、意大利语、葡萄牙语)
    """
    text_lower = text.lower()
    
    # 西班牙语特征词
    spanish_patterns = [
        r'\b(el|la|los|las|un|una|de|en|que|es|se|no|te|lo|le|da|su|por|son|con|para|al|del|está|todo|pero|más|hacer|muy|puede|tiempo|si|él|sobre|mi|estar|entre|sin|hasta|desde|cuando|mucho|también|año|años|día|días|vida|mundo|casa|parte|lugar|trabajo|hombre|mujer|niño|niña)\b'
    ]
    
    # 法语特征词
    french_patterns = [
        r'\b(le|la|les|un|une|de|du|des|et|à|il|être|avoir|que|ce|se|qui|pour|dans|par|sur|avec|ne|son|sa|ses|tout|mais|comme|faire|plus|dire|aller|voir|savoir|prendre|venir|falloir|vouloir|pouvoir|grand|petit|autre|même|nouveau|premier|dernier|bon|mauvais|beau|jeune|vieux|blanc|noir|rouge|vert|bleu|jaune)\b'
    ]
    
    # 意大利语特征词
    italian_patterns = [
        r'\b(il|lo|la|i|gli|le|un|uno|una|di|a|da|in|con|su|per|tra|fra|che|e|o|ma|se|quando|dove|come|perché|chi|cosa|quale|quanto|molto|poco|tutto|niente|sempre|mai|già|ancora|qui|qua|lì|là|oggi|ieri|domani|ora|adesso|prima|dopo|sopra|sotto|dentro|fuori|davanti|dietro|accanto|vicino|lontano)\b'
    ]
    
    # 葡萄牙语特征词
    portuguese_patterns = [
        r'\b(o|a|os|as|um|uma|de|da|do|das|dos|em|na|no|nas|nos|para|por|com|sem|sobre|entre|até|desde|quando|onde|como|que|se|não|sim|mas|ou|e|também|muito|pouco|todo|nada|sempre|nunca|já|ainda|aqui|ali|lá|hoje|ontem|amanhã|agora|antes|depois|cima|baixo|dentro|fora|frente|atrás|lado|perto|longe)\b'
    ]
    
    # 计算每种语言的匹配分数
    spanish_score = len(re.findall('|'.join(spanish_patterns), text_lower))
    french_score = len(re.findall('|'.join(french_patterns), text_lower))
    italian_score = len(re.findall('|'.join(italian_patterns), text_lower))
    portuguese_score = len(re.findall('|'.join(portuguese_patterns), text_lower))
    
    scores = {
        'es': spanish_score,
        'fr': french_score,
        'it': italian_score,
        'pt': portuguese_score
    }
    
    max_score = max(scores.values())
    if max_score > 0:
        return max(scores, key=scores.get)
    
    return None

def detect_german(text):
    """
    检测德语特征
    """
    text_lower = text.lower()
    german_patterns = [
        r'\b(der|die|das|den|dem|des|ein|eine|einen|einem|einer|eines|und|oder|aber|doch|jedoch|sondern|denn|weil|da|wenn|als|wie|wo|woher|wohin|wann|warum|weshalb|wieso|was|wer|wen|wem|wessen|welcher|welche|welches|dieser|diese|dieses|jener|jene|jenes|ich|du|er|sie|es|wir|ihr|sie|mich|dich|ihn|uns|euch|mir|dir|ihm|ihr|ihnen|mein|dein|sein|unser|euer|haben|sein|werden|können|müssen|sollen|wollen|dürfen|mögen|lassen|gehen|kommen|machen|sagen|sehen|wissen|denken|glauben|finden|geben|nehmen|bringen|halten|stehen|liegen|sitzen|leben|arbeiten|spielen|lernen|verstehen|sprechen|hören|lesen|schreiben|kaufen|verkaufen|essen|trinken|schlafen|aufstehen|anziehen|ausziehen)\b'
    ]
    
    german_score = len(re.findall('|'.join(german_patterns), text_lower))
    return 'de' if german_score > 0 else None