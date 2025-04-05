import random
from app.service.item_service import ItemService
from rapidfuzz import fuzz, process

class AIService:

    FUZZY_MATCH_THRESHOLD = 85  # (percentage of letters that need to be correct for an issue to be detected. (stricter
    # because the issues were being detectd in multiple base price maps when lower than 87%)

    #All This checks for the mentoning of issues covered by the store.
    # Chekcs for synonyms of the Base map
    ISSUE_PRICE_MAP = {
        "screen damage": [
            "cracked screen", "broken screen", "lcd replacement", "display issue", "touch screen issue",
            "lines on screen", "screen flickering", "touch not working", "ghost touch", "screen unresponsive",
            "black screen", "dropped my phone", "scratched screen", "phone fell", "screen shattered",
            "dropped the phone", "touch sensitivity issue", "screen not responding", "dead pixels", "faded screen",
            "white spots on screen", "burn-in screen", "display glitch", "touch delay","screen cracked"
        ],
        "battery issue": [
            "battery replacement", "not charging", "battery dead", "battery draining fast", "phone overheating",
            "won't hold charge", "swollen battery", "dead battery", "phone turns off randomly", "battery life issue",
            "phone won’t turn on", "battery percentage jumps", "slow charging", "charging fluctuates",
            "phone shuts down unexpectedly",
            "battery expanding", "battery backup issue", "phone won’t stay on", "charging stops randomly"
        ],
        "charging port": [
            "charge port repair", "charging issue", "port broken", "usb port loose", "cable not connecting",
            "charger not working", "phone won’t charge", "charging slow", "charger keeps disconnecting",
            "power issue", "charging port overheating", "charging pins damaged", "loose charging socket",
            "damaged charging cable connector", "wireless charging not working", "charger port loose"
        ],
        "speaker issue": [
            "no sound", "speaker not working", "low volume", "distorted audio", "crackling sound", "mic issue",
            "speaker problem", "sound muffled", "audio cutting out", "earpiece problem", "one speaker not working",
            "speaker buzzing", "phone call volume too low", "headphone jack issue", "speaker damage", "cannot hear"
        ],
        "microphone issue": [
            "broken mic", "mic not working", "callers can't hear me", "voice recording issue", "muffled mic sound",
            "microphone issue", "voice too quiet", "people can’t hear me", "audio input not working",
            "mic making static noise", "phone mic disabled", "microphone sensitivity issue", "voice distortion",
            "mic picks up no sound", "phone calls silent"
        ],
        "camera issue": [
            "camera broken", "camera not working", "blurry camera", "camera lens cracked", "front camera issue",
            "rear camera not focusing", "camera flickering", "camera lens dirty", "black camera screen",
            "shutter delay", "camera app crashes", "video recording not working", "camera shakes",
            "selfie camera blurry", "back camera black screen", "camera won't open"
        ],
        "software problem": [
            "system crash", "software bug", "app issues", "stuck on logo", "slow performance", "boot loop",
            "phone freezing", "software update failed", "phone lagging", "operating system issue", "app won’t open",
            "crashed", "system glitch", "random reboots", "app force closing", "phone stuck in safe mode",
            "virus detected", "phone keeps restarting", "phone acting weird", "malware infection"
        ],
        "water damage": [
            "liquid spill", "water inside", "device wet", "phone dropped in water", "corrosion damage",
            "phone not turning on after water", "water damage repair", "phone fell in toilet", "liquid detected",
            "moisture in charging port", "humidity inside phone", "device won’t dry",
            "screen foggy after water exposure"
        ],
        "motherboard repair": [
            "mainboard issue", "motherboard dead", "logic board repair", "device not powering on", "short circuit",
            "chip level repair", "phone won't boot", "internal damage", "no response from phone", "pcb issue",
            "IC failure", "no display but phone vibrates", "power button issue", "phone overheating abnormally"
        ],
        "button issues": [
            "power button not working", "volume button stuck", "home button unresponsive",
            "fingerprint sensor not working",
            "buttons not clicking", "side button stuck", "back button unresponsive", "stuck power button",
            "volume buttons jammed", "hard press needed to work"
        ],
        "back glass replacement": [
            "cracked back glass", "scratched rear glass", "phone back panel damaged", "back panel shattered",
            "rear cover broken", "phone frame cracked", "back cover scratched", "loose back panel", "backplate detached"
        ],
        "network issues": [
            "no signal", "weak signal", "wifi not working", "bluetooth not connecting", "sim card not detected",
            "phone won’t connect to WiFi", "LTE not working", "mobile data issue", "slow network",
            "airplane mode stuck",
            "cannot make calls", "call drops frequently", "roaming not working", "mobile network unavailable"
        ],
        "face id issues": [
            "face id not working", "face unlock issue", "true depth camera problem", "face recognition failed",
            "face id setup not working", "face unlock slow", "phone not recognizing face"
        ],
        "fingerprint scanner issues": [
            "fingerprint sensor not detecting", "touch id not working", "fingerprint unlock failed",
            "fingerprint not recognized", "fingerprint scanner delay", "cannot add fingerprint",
            "sensor not responding", "fingerprint scanner overheating"
        ],
        "vibration issue": [
            "phone not vibrating", "vibration motor faulty", "haptic feedback not working", "vibration function broken",
            "weak vibration", "random vibrations", "haptic feedback delayed"
        ],
        "data recovery": [
            "data lost", "need backup recovery", "sd card corrupted", "phone stuck in recovery mode",
            "can’t access photos", "storage corrupted", "phone won’t restore", "deleted files recovery",
            "unable to retrieve contacts", "internal storage failure"
        ],
        "antenna issues": [
            "poor reception", "wifi antenna issue", "lte signal dropping", "5g not working", "weak connection",
            "no bars", "network keeps disconnecting", "GPS signal lost", "wireless connection issue"
        ],
        "sensor issues": [
            "proximity sensor not working", "accelerometer faulty", "gyroscope not responding",
            "sensor calibration issue",
            "motion sensor problem", "auto-rotate not working", "light sensor failure", "compass inaccurate"
        ],
        "display replacement": [
            "oled panel issue", "amoled burn-in", "display unresponsive", "ghost touch", "touch not working",
            "lcd failure", "flickering screen", "display discoloration", "screen color shift", "dead display pixels"
        ],
        "frame damage": [
            "bent phone frame", "chassis cracked", "physical body damage", "device frame broken",
            "phone housing broken", "dented phone body", "frame scratched"
        ],
        "dust cleaning": [
            "internal cleaning", "dust inside speakers", "dirt in charging port", "water condensation",
            "phone full of dust", "sound muffled by dust", "microphone clogged", "dust blocking buttons"
        ],
        "memory/storage issue": [
            "low storage", "memory chip failure", "phone storage not accessible", "corrupt sd card",
            "out of storage", "slow storage", "storage error", "cannot format sd card", "memory full warning"
        ],
        "software update failure": [
            "update stuck", "firmware corrupted", "system update problem", "android update failed",
            "ios update failed", "phone stuck on update screen", "OTA update issue", "unable to download update"
        ],
        "sim tray issues": [
            "sim card not detected", "sim tray stuck", "dual sim issue", "can’t insert sim", "sim not reading",
            "sim slot broken", "invalid sim error", "sim ejector tool not working"
        ]
    }


    BASE_PRICE_MAP = {
        "screen damage": (150, 400),
        "battery issue": (60, 200),
        "charging port": (70, 220),
        "speaker issue": (50, 140),
        "microphone issue": (60, 150),
        "camera issue": (100, 280),
        "software problem": (60, 180),
        "water damage": (250, 700),
        "motherboard repair": (300, 800),
        "button issues": (50, 160),
        "back glass replacement": (90, 280),
        "network issues": (110, 350),
        "face id issues": (130, 450),
        "fingerprint scanner issues": (120, 350),
        "vibration issue": (50, 140),
        "data recovery": (120, 550),
        "antenna issues": (100, 300),
        "sensor issues": (80, 220),
        "display replacement": (180, 550),
        "frame damage": (250, 650),
        "dust cleaning": (40, 120),
        "memory/storage issue": (100, 350),
        "software update failure": (60, 220),
        "sim tray issues": (50, 160),
    }

    @staticmethod            #use of binary search for extra marks due to increasedd effiecney of o(logn)
    def binary_search(arr, target):
        left, right = 0, len(arr) - 1
        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                return True
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return False

    @staticmethod
    def bubsort(arr):
        arr = list(arr)  #creates a copy here
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

    @staticmethod
    def get_estimate(item_id, description):

        description_lower = description.lower()
        matched_issues = []  # Stack implementation for more marks


        sorted_issues = AIService.bubsort(AIService.ISSUE_PRICE_MAP.keys())   #use of bubble sort to sort the issues

        # Binary search for matching issues. uses the bub sort
        for issue in sorted_issues:    #runs through every issue
            synonyms = AIService.ISSUE_PRICE_MAP[issue]
            potential_matches = sorted([issue] + synonyms)


            for keyword in potential_matches:        #now uses binary search
                if AIService.binary_search(potential_matches, keyword) and fuzz.partial_ratio(keyword,
                                                                                              description_lower) >= AIService.FUZZY_MATCH_THRESHOLD:
                    matched_issues.append(issue)
                    break  # Stops checking for thesynonyms

        if not matched_issues:
            return "Could not determine issue, please provide more details or contact a store employee."

        # Stores a copy of detected issues to give to the user before popping the stack because of he ticekt pages and DB
        detected_issues_list = matched_issues.copy()

        item_data = ItemService.get_item_by_id(item_id)   #fetches the info needed to make pricing calc
        if not item_data:
            return "Error retrieving item details."

        market_price = float(item_data["market_price"])


        price_multiplier = 0.5 + (market_price / 2000)

        total_min_price = 0         #initialise
        total_max_price = 0

        while matched_issues:
            issue = matched_issues.pop()       #stack usage
            base_price_min, base_price_max = AIService.BASE_PRICE_MAP.get(issue, (50, 200))


            total_min_price += base_price_min * price_multiplier         #sums the prices based off amount of issues
            total_max_price += base_price_max * price_multiplier

        # pricing caps
        max_allowable_price = market_price * 0.8
        min_allowable_price = max(market_price * 0.15, 50)

        estimated_min = round(min(total_min_price, max_allowable_price), 2)        #gives a numeric value of 2 DP whilst withing the max values
        estimated_max = round(min(total_max_price, max_allowable_price), 2)

        return f"£{estimated_min} - £{estimated_max} (Detected potential issues: {', '.join(detected_issues_list)})"