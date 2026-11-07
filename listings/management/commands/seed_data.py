from django.core.management.base import BaseCommand

from listings.models import Course, University

DATA = {
    "APJ Abdul Kalam Technological University (KTU)": [
        "B.Tech CSE", "B.Tech ECE", "B.Tech EEE",
        "B.Tech Mechanical", "B.Tech Civil",
    ],
    "Mahatma Gandhi University": [
        "B.Sc Computer Science", "BCA", "B.Com", "B.Sc Mathematics", "BA English",
    ],
    "University of Calicut": [
        "B.Sc Computer Science", "BCA", "B.Com", "B.Sc Mathematics", "BA English",
    ],
    "University of Kerala": [
        "B.Sc Computer Science", "BCA", "B.Com", "B.Sc Mathematics", "BA English",
    ],
    "Kannur University": [
        "B.Sc Computer Science", "BCA", "B.Com", "B.Sc Mathematics", "BA English",
    ],
    "Cochin University of Science and Technology (CUSAT)": [
        "B.Tech CSE", "B.Tech ECE", "B.Tech Mechanical",
    ],
    "Kerala University of Health Sciences (KUHS)": [
        "MBBS", "BDS", "BAMS", "BHMS", "B.Sc Nursing",
        "B.Pharm", "Pharm.D", "BPT",
    ],
    "Kerala Agricultural University": [
        "B.Sc (Hons) Agriculture", "B.Sc (Hons) Forestry",
        "B.Sc (Hons) Cooperation and Banking Management",
        "B.Tech Agricultural Engineering", "B.Tech Food Technology",
    ],
    "Kerala University of Fisheries and Ocean Studies (KUFOS)": [
        "B.F.Sc (Fisheries Science)",
    ],
    "Kerala Veterinary and Animal Sciences University": [
        "B.V.Sc & A.H.", "B.Tech Dairy Technology", "B.Tech Food Technology",
    ],
    "National University of Advanced Legal Studies (NUALS)": [
        "BA LLB (Hons)", "LLM",
    ],
}


class Command(BaseCommand):
    help = "Create Kerala universities and common courses (safe to run many times)."

    def handle(self, *args, **options):
        for uni_name, course_names in DATA.items():
            university, _ = University.objects.get_or_create(name=uni_name)
            for course_name in course_names:
                Course.objects.get_or_create(university=university, name=course_name)
        self.stdout.write(self.style.SUCCESS(
            f"Done. {University.objects.count()} universities, "
            f"{Course.objects.count()} courses."
        ))