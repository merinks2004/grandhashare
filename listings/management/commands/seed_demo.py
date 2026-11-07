import io
import textwrap

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from accounts.models import Profile
from listings.models import BookImage, Course, Listing

UNI = {
    "KTU": "APJ Abdul Kalam Technological University (KTU)",
    "MG": "Mahatma Gandhi University",
    "CU": "University of Calicut",
    "KER": "University of Kerala",
    "CUSAT": "Cochin University of Science and Technology (CUSAT)",
    "KUHS": "Kerala University of Health Sciences (KUHS)",
    "NUALS": "National University of Advanced Legal Studies (NUALS)",
    "KAN": "Kannur University",
    "KAU": "Kerala Agricultural University",
    "KVASU": "Kerala Veterinary and Animal Sciences University",
}

COLORS = ["#0f766e", "#1d4ed8", "#9333ea", "#b45309", "#be123c", "#047857", "#334155"]


def make_cover(title, author, color):
    img = Image.new("RGB", (400, 560), color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 380, 540], outline="white", width=4)
    title_font = ImageFont.load_default(size=34)
    small_font = ImageFont.load_default(size=22)
    y = 80
    for line in textwrap.wrap(title, width=16):
        draw.text((200, y), line, font=title_font, fill="white", anchor="ma")
        y += 44
    draw.text((200, 490), author[:28], font=small_font, fill="white", anchor="ma")
    buffer = io.BytesIO()
    img.save(buffer, "JPEG", quality=85)
    return ContentFile(buffer.getvalue())

# (title, author, subject, university, course, semester, condition, type, price)
BOOKS = [
    ("Higher Engineering Mathematics", "B.S. Grewal", "Mathematics", "KTU", "B.Tech CSE", 1, "good", "sell", 250),
    ("Data Structures Using C", "Reema Thareja", "Data Structures", "KTU", "B.Tech CSE", 3, "like_new", "sell", 300),
    ("Operating System Concepts", "Silberschatz, Galvin, Gagne", "Operating Systems", "KTU", "B.Tech CSE", 4, "good", "sell", 350),
    ("Computer Organization and Architecture", "William Stallings", "Computer Organization", "KTU", "B.Tech CSE", 3, "fair", "swap", 0),
    ("Database System Concepts", "Silberschatz, Korth, Sudarshan", "DBMS", "KTU", "B.Tech CSE", 5, "good", "sell", 400),
    ("Computer Networks", "Andrew S. Tanenbaum", "Computer Networks", "KTU", "B.Tech CSE", 6, "like_new", "sell", 380),
    ("Digital Design", "M. Morris Mano", "Digital Electronics", "KTU", "B.Tech ECE", 3, "good", "sell", 220),
    ("Electronic Devices and Circuit Theory", "Boylestad, Nashelsky", "Electronics", "KTU", "B.Tech ECE", 3, "fair", "donate", 0),
    ("Signals and Systems", "Alan V. Oppenheim", "Signals and Systems", "KTU", "B.Tech ECE", 4, "good", "sell", 300),
    ("Fluid Mechanics and Hydraulic Machines", "R.K. Bansal", "Fluid Mechanics", "KTU", "B.Tech Mechanical", 4, "good", "sell", 280),
    ("Let Us C", "Yashavant Kanetkar", "C Programming", "MG", "BCA", 1, "good", "sell", 150),
    ("Object Oriented Programming with C++", "E. Balagurusamy", "C++", "MG", "BCA", 2, "like_new", "sell", 180),
    ("Programming in ANSI C", "E. Balagurusamy", "C Programming", "MG", "B.Sc Computer Science", 1, "fair", "donate", 0),
    ("Thomas' Calculus", "George B. Thomas", "Calculus", "MG", "B.Sc Mathematics", 2, "good", "swap", 0),
    ("Financial Management", "I.M. Pandey", "Financial Management", "MG", "B.Com", 4, "good", "sell", 200),
    ("Let Us C", "Yashavant Kanetkar", "C Programming", "CU", "BCA", 1, "good", "sell", 140),
    ("Programming in ANSI C", "E. Balagurusamy", "C Programming", "CU", "B.Sc Computer Science", 1, "like_new", "sell", 170),
    ("Financial Management", "I.M. Pandey", "Financial Management", "CU", "B.Com", 4, "fair", "sell", 160),
    ("Thomas' Calculus", "George B. Thomas", "Calculus", "CU", "B.Sc Mathematics", 2, "good", "sell", 220),
    ("Introduction to Algorithms", "Cormen et al.", "Algorithms", "KER", "B.Sc Computer Science", 5, "good", "sell", 450),
    ("Object Oriented Programming with C++", "E. Balagurusamy", "C++", "KER", "BCA", 2, "good", "donate", 0),
    ("Computer Networks", "Andrew S. Tanenbaum", "Computer Networks", "CUSAT", "B.Tech CSE", 6, "good", "sell", 350),
    ("Gray's Anatomy for Students", "Drake, Vogl, Mitchell", "Anatomy", "KUHS", "MBBS", 1, "good", "sell", 900),
    ("Essentials of Medical Pharmacology", "K.D. Tripathi", "Pharmacology", "KUHS", "MBBS", 3, "like_new", "sell", 700),
    ("Constitutional Law of India", "J.N. Pandey", "Constitutional Law", "NUALS", "BA LLB (Hons)", 3, "good", "sell", 400),
        ("Basic Electrical Engineering", "D.P. Kothari", "Electrical Engineering", "KTU", "B.Tech EEE", 1, "good", "sell", 200),
    ("Power System Analysis", "Hadi Saadat", "Power Systems", "KTU", "B.Tech EEE", 5, "good", "sell", 320),
    ("Engineering Mechanics", "S.S. Bhavikatti", "Mechanics", "KTU", "B.Tech Civil", 1, "fair", "sell", 150),
    ("Strength of Materials", "R.K. Bansal", "Strength of Materials", "KTU", "B.Tech Civil", 3, "good", "sell", 260),
    ("Thermodynamics: An Engineering Approach", "Yunus Cengel", "Thermodynamics", "KTU", "B.Tech Mechanical", 3, "good", "sell", 350),
    ("Theory of Machines", "S.S. Rattan", "Theory of Machines", "KTU", "B.Tech Mechanical", 5, "like_new", "sell", 300),
    ("Discrete Mathematical Structures", "Bernard Kolman", "Discrete Mathematics", "KTU", "B.Tech CSE", 3, "good", "swap", 0),
    ("Introduction to the Design and Analysis of Algorithms", "Anany Levitin", "Algorithms", "KTU", "B.Tech CSE", 5, "like_new", "sell", 330),
    ("Compilers: Principles, Techniques, and Tools", "Aho, Lam, Sethi, Ullman", "Compiler Design", "KTU", "B.Tech CSE", 6, "good", "sell", 340),
    ("Microprocessor Architecture, Programming and Applications", "Ramesh Gaonkar", "Microprocessors", "KTU", "B.Tech ECE", 4, "good", "donate", 0),
    ("Python Crash Course", "Eric Matthes", "Python", "MG", "BCA", 3, "like_new", "sell", 250),
    ("Java: The Complete Reference", "Herbert Schildt", "Java", "MG", "BCA", 4, "good", "sell", 300),
    ("Database Management Systems", "Raghu Ramakrishnan", "DBMS", "CU", "BCA", 3, "good", "sell", 280),
    ("Financial Accounting", "S.N. Maheshwari", "Accounting", "CU", "B.Com", 1, "good", "sell", 150),
    ("Business Statistics", "S.P. Gupta", "Statistics", "MG", "B.Com", 2, "fair", "donate", 0),
    ("Advanced Engineering Mathematics", "Erwin Kreyszig", "Engineering Mathematics", "KER", "B.Sc Mathematics", 3, "good", "sell", 300),
    ("Principles of Mathematical Analysis", "Walter Rudin", "Real Analysis", "CU", "B.Sc Mathematics", 4, "good", "swap", 0),
    ("A Passage to India", "E.M. Forster", "English Literature", "KAN", "BA English", 2, "good", "sell", 100),
    ("Literary Theory: An Introduction", "Terry Eagleton", "Literary Theory", "KAN", "BA English", 5, "like_new", "sell", 220),
    ("Computer Networking: A Top-Down Approach", "Kurose and Ross", "Computer Networks", "CUSAT", "B.Tech CSE", 5, "good", "sell", 360),
    ("Fundamentals of Nursing", "Potter and Perry", "Nursing Foundations", "KUHS", "B.Sc Nursing", 1, "good", "sell", 450),
    ("Pharmacognosy", "C.K. Kokate", "Pharmacognosy", "KUHS", "B.Pharm", 3, "good", "sell", 250),
    ("Dental Anatomy, Physiology and Occlusion", "Wheeler", "Dental Anatomy", "KUHS", "BDS", 1, "fair", "sell", 500),
    ("Principles of Agronomy", "S.R. Reddy", "Agronomy", "KAU", "B.Sc (Hons) Agriculture", 2, "good", "sell", 220),
    ("Textbook of Veterinary Physiology", "Cunningham", "Veterinary Physiology", "KVASU", "B.V.Sc & A.H.", 2, "good", "sell", 600),
]


class Command(BaseCommand):
    help = "Create demo sellers and demo books. Use --clear to remove them."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Delete all demo data")

    def handle(self, *args, **options):
        if options["clear"]:
            deleted, _ = User.objects.filter(username__startswith="demo_").delete()
            self.stdout.write(self.style.SUCCESS(f"Removed demo data ({deleted} rows)."))
            return

        sellers = []
        for i in range(1, 6):
            user, created = User.objects.get_or_create(
                username=f"demo_senior{i}",
                defaults={"email": f"demo_senior{i}@example.com"},
            )
            if created:
                user.set_unusable_password()
                user.save()
            Profile.objects.get_or_create(
                user=user, defaults={"phone": "0000000000", "college": "Demo College"}
            )
            sellers.append(user)

        added = skipped = 0
        for n, (title, author, subject, uni, course_name, sem, cond, kind, price) in enumerate(BOOKS):
            course = Course.objects.filter(
                name=course_name, university__name=UNI[uni]
            ).first()
            if not course:
                skipped += 1
                continue
            listing, created = Listing.objects.get_or_create(
                seller=sellers[n % len(sellers)],
                title=title,
                course=course,
                defaults={
                    "author": author,
                    "subject": subject,
                    "semester": sem,
                    "condition": cond,
                    "listing_type": kind,
                    "price": price,
                    "description": "Sample listing for demonstration.",
                },
            )
            added += created
            if not listing.images.exists():
                cover = BookImage(listing=listing)
                cover.image.save(
                    f"demo_{listing.pk}.jpg",
                    make_cover(title, author, COLORS[n % len(COLORS)]),
                    save=True,
                )

        self.stdout.write(self.style.SUCCESS(
            f"Demo books added: {added}. Skipped (course missing): {skipped}."
        ))