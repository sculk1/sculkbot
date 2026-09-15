# ==============================================================================
# TIER 1: TITLES (Global, Japanese, and Localized)
# Trigger: INSTANT PING (100% confidence)
# ==============================================================================
TITLES = [
    # English & Acronyms
    "cosmic princess kaguya",
    "princess kaguya",
    "cpk",

    # Japanese & Romaji
    "超かぐや姫",
    "超かぐや姫！",
    "cho kaguya-hime",
    "cho kaguyahime",
    "chō kaguya-hime",
    "chō kaguyahime",
    "cho kaguya hime",
    "super kaguya hime",

    # Spanish
    "la princesa kaguya del cosmos",

    # Arabic (stripped of RTL marks)
    "كاغويا أميرة الفضاء",

    # Chinese
    "超时空辉耀姬",
    "超時空輝耀姬",

    # French
    "kaguya princesse cosmique",
    "kaguya, princesse cosmique",

    # Greek
    "κοσμική πριγκίπισσα καγκούγια",

    # Korean
    "초 가구야 공주",
    "초(超) 가구야 공주",
    "초가구야 공주",

    # Portuguese
    "kaguya a princesa espacial",
    "kaguya: a princesa espacial",

    # Romanian
    "cosmica prințesă kaguya",
    "cosmica printesa kaguya",

    # Thai
    "เจ้าหญิงกระบอกไม้ไผ่ ในโลกเมตาเวิร์ส",
    "เจ้าหญิงกระบอกไม้ไผ่ในโลกเมตาเวิร์ส",

    # Russian
    "космическая принцесса кагуя",

    # Hebrew
    "הנסיכה הקוסמית קאגויה",

    # Vietnamese
    "kaguya - công chúa vũ trụ",
    "kaguya công chúa vũ trụ",

    # Polish
    "kosmiczna księżniczka kaguya",

    # Italian
    "kaguya principessa cosmica"
]


# ==============================================================================
# TIER 2: UNAMBIGUOUS CPK REFERENCES
# Trigger: INSTANT PING (These names ONLY exist in Cosmic Princess Kaguya)
# ==============================================================================
UNAMBIGUOUS_CPK_REF = [
    # Main Characters (Full Names / Unique spellings)
    "iroha sakayori",
    "sakayori iroha",
    "iroha",
    "sakayori",
    "酒寄彩葉",
    "さかよりいろは",
    
    "yachiyo runami",
    "runami yachiyo",
    "tsukimi yachiyo",
    "yachiyo tsukimi",
    "yachiyo",
    "runami",
    "月見八千代",
    "瑠波八千代",

    # Supporting / Rival Characters
    "akira mikado",
    "帝アキラ",
    "rai komazawa",
    "noi komazawa",
    "駒沢ライ",
    "駒沢ノイ",
    "roka ayatsumugi",
    "綾紡ロカ",
    "mami isayama",
    "諫山マミ",
    "koto okkotteru",
    "落照コト",

    # Production Studio
    "studio chromato",
    "chromato studio"

    "cho-kaguya-hime",
    "cho-kaguyahime",
    "cho kaguya hime",
    "chō kaguya hime",
    "chō kaguyahime",
    "chō kaguya-hime",
    "chokaguyahime"
]


# ==============================================================================
# TIER 3: MOST CERTAINLY CPK (High-Probability Compound Phrases)
# Trigger: PING (Unless negative filters are hit)
# ==============================================================================
MOST_CERTAINLY_CPK = [
    # Metaverse & World Terminology
    "tsukuyomi metaverse",
    "tsukuyomi virtual world",
    "tsukuyomi streamer",
    "tsukuyomi anime",
    "mundo tsukuyomi",

    # Unique Plot Elements
    "kaguya utility pole",
    "kaguya telephone pole",
    "baby in the utility pole",
    "bamboo cutter metaverse",
    "metaverse kaguya",
    "kaguya",

    # Staff / Creator Pairings
    "shingo yamashita kaguya",
    "yamashita shingo kaguya",
    "studio colorido kaguya",
    "colorido kaguya"
]


# ==============================================================================
# TIER 4: NEGATIVE EXCLUSIONS (False Positive Blockers)
# Trigger: If these appear alongside generic "kaguya", DO NOT PING.
# ==============================================================================
NEGATIVE_EXCLUSIONS = [
    # Kaguya-sama: Love is War
    "love is war",
    "shinomiya",
    "shirogane",
    "chika fujiwara",
    "ishigami",
    "miko iino",
    "hayasaka",
    "aka akasaka",

    # Naruto / Boruto
    "otsutsuki",
    "ōtsutsuki",
    "naruto",
    "boruto",
    "madara",
    "hagoromo",
    "hamura",
    "chakra fruit",
    "infinite tsukuyomi",  # Note: Prevents Naruto's Infinite Tsukuyomi from colliding with CPK's Tsukuyomi

    # Touhou Project
    "houraisan",
    "mokou",
    "eirin",
    "inaba"
]