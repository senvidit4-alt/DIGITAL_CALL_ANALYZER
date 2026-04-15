"""
models/scam_patterns.py
=======================
All scam detection data lives here.
P1 can update keywords independently without touching any logic code.
"""

SCAM_STAGES = ["Authority", "Fear", "Isolation", "Urgency", "Extract"]

SCAM_KEYWORDS = {
    "Authority": [
        "police", "customs", "cbi", "rbi", "fedex", "trai", "sir",
        "officer", "inspector", "department", "narcotics", "court",
        " ed ", "income tax", "cyber cell", "headquarters",
    ],
    "Fear": [
        "arrest", "warrant", "jail", "criminal", "money laundering",
        "raid", "notice", "fir", "illegal", "suspend", "penalty",
        "fine", "case", "smuggling", "drugs", "passport", "seize",
        "freeze", "defamation", "block",
        "गिरफ्तार", "वारंट", "जेल", "केस", "जुर्माना", "सजा", "अपराध",
    ],
    "Isolation": [
        "kisi ko mat batana", "secret", "confidential", "line pe rahiye",
        "call mat kaatna", "akele me jao", "headphones lagao",
        "door band karo", "akela", "kisi se baat mat karna", "isolate",
        "shor nahi hona chahiye",
        "किसी को मत बताना", "लाइन पर रहिए", "कॉल मत काटना", "अकेले",
    ],
    "Urgency": [
        "immediately", "right now", "jaldi", "urgent", "24 hours",
        "turant", "abhi ke abhi", "action lenge", "aaj hi", "abhi",
        "last chance", "expire", "तुरन्त", "अभी", "जल्दी", "फौरन",
    ],
    "Extract": [
        "otp", "transfer", "paise", "account", "wallet", "crypto",
        "gift card", "insurance", "cvv", "pin", "anydesk", "teamviewer",
        "screen share", "upi", "password", "bank details", "aadhar",
        "pan", "kyc", "rtgs", "neft",
        "ओटीपी", "पैसे", "अकाउंट", "खाता", "पासवर्ड", "आधार",
    ],
}

ESCAPE_SCRIPTS = {
    "Authority": (
        "Acknowledge politely, then say: 'I need to consult my lawyer before discussing this.' Hang up."
    ),
    "Fear": (
        "Say: 'My network is dropping, I cannot hear you.' "
        "Hang up and verify by calling the official department number."
    ),
    "Isolation": (
        "Say: 'Someone is at the door, I have to open it.' "
        "Hang up immediately. Never stay isolated on a call."
    ),
    "Urgency": (
        "Say: 'I am driving right now and cannot process anything.' "
        "Hang up. True officials never force immediate action over phone."
    ),
    "Extract": (
        "DO NOT share OTP or download any app. "
        "Say: 'I will visit my local bank branch physically.' Hang up and block the number."
    ),
    "Unknown": (
        "If you feel suspicious, say 'I cannot talk right now' and disconnect immediately."
    ),
}
