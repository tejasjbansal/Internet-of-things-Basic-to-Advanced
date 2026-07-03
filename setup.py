import os

# (folder number, title, lecture count)
sections = [
    (1, "IoT for Industry 4.0 – Course Outline & Getting Started", 3),
    (2, "IoT Fundamentals, Architecture & Challenges", 12),
    (3, "Introduction to Industry 4.0", 5),
    (4, "Hands-on Lab – MQTT Communication", 6),
    (5, "Hands-On AIoT Pipeline in Python", 7),
    (6, "IoT Devices, Cloud and Edge Computing", 7),
    (7, "IoT Networking Protocol and Application", 8),
    (8, "IoT Cloud Processing with AWS IoT Core & DynamoDB", 4),
    (9, "IoT Cloud Stream Processing – AWS IoT Core, Kinesis, DynamoDB", 4),
    (10, "IoT Cloud Batch Processing – AWS SageMaker & Spark", 2),
    (11, "Connecting Dots (Guided Projects)", 5),
    (12, "Capstone Project", 2),
    (13, "Cybersecurity in IoT and AI-enabled IoT Systems", 6),
    (14, "Cloud-Based AIoT Systems", 10),
    (15, "AI-ML Workflows for IoT", 12),
    (16, "AI and Machine Learning for AIoT – Hands-on Lab", 7),
    (17, "Edge AI and TinyML", 6),
    (18, "Edge AI and TinyML – Hands-On", 2),
]

# Base directory where course folders will be created.
# Change this to any path you like, or leave as "." for current directory.
BASE_DIR = "."


def sanitize(name: str) -> str:
    """Remove characters that are invalid in folder names on most OSes."""
    invalid_chars = '<>:"/\\|?*'
    for ch in invalid_chars:
        name = name.replace(ch, "-")
    return name.strip()


def main():
    os.makedirs(BASE_DIR, exist_ok=True)

    for number, title, lecture_count in sections:
        folder_name = sanitize(f"{number:02d} - {title} ({lecture_count} lectures)")
        folder_path = os.path.join(BASE_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        print(f"Created: {folder_path}")

    print(f"\nDone! Created {len(sections)} folders in '{os.path.abspath(BASE_DIR)}'.")


if __name__ == "__main__":
    main()