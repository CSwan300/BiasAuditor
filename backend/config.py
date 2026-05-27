# Constants and global configurations
PROTECTED_KEYWORDS = ["age", "gender", "ethnicity", "race", "sex", "nationality", "religion"]
OUTCOME_KEYWORDS = ["prediction", "result", "label", "outcome", "target", "hired", "approved",
                    "accepted", "selected", "score", "decision"]

AGE_BINS = [0, 17, 29, 44, 59, 74, 150]
AGE_LABELS = ["<18", "18-29", "30-44", "45-59", "60-74", "75+"]

MIN_GROUP_SIZE = 5  # Groups smaller than this are flagged as insufficient