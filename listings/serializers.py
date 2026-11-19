from rest_framework import serializers

from .models import Course, Listing, University


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ["id", "name"]


class CourseSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source="university.name", read_only=True)

    class Meta:
        model = Course
        fields = ["id", "name", "university", "university_name"]


class ListingSerializer(serializers.ModelSerializer):
    listing_code = serializers.SerializerMethodField()
    seller_username = serializers.CharField(source="seller.username", read_only=True)
    course_name = serializers.CharField(source="course.name", read_only=True)
    university_name = serializers.CharField(source="course.university.name", read_only=True)
    is_demo = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "id", "listing_code", "title", "author", "edition", "subject",
            "course", "course_name", "university_name", "semester",
            "condition", "listing_type", "price", "status", "description",
            "date_posted", "seller_username", "is_demo", "images",
        ]
        read_only_fields = ["status", "date_posted"]

    def get_listing_code(self, obj):
        return f"GS-{obj.pk:05d}"

    def get_is_demo(self, obj):
        return obj.seller.username.startswith("demo_")

    def get_images(self, obj):
        request = self.context.get("request")
        urls = []
        for img in obj.images.all():
            url = img.image.url
            if request:
                url = request.build_absolute_uri(url)
            urls.append(url)
        return urls

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate(self, data):
        if data.get("listing_type") == "donate":
            data["price"] = 0
        return data