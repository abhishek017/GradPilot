from django.db import models
from django.utils import timezone 
from ceremony.utils import process_photo
from PIL import Image
import os
from django.templatetags.static import static



class Graduate(models.Model):
    # Original / imported columns
    submission_date = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    qualification = models.CharField(max_length=100, null=True, blank=True)
    student_id = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50, blank=True)
    gown_option = models.CharField(
        max_length=50,
        blank=True,
        help_text='Hire or Purchase from form',
    )
    additional_guests = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unique_id = models.CharField(max_length=50, unique=True)
    gown_size = models.CharField(max_length=20, blank=True)
    submission_id = models.CharField(max_length=50, blank=True)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)

    # Event-control fields
    attended = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.CharField(max_length=100, blank=True)

    gown_collected = models.BooleanField(default=False)
    gown_returned = models.BooleanField(default=False)
    gown_notes = models.TextField(blank=True)

    seat_row = models.CharField(max_length=10, blank=True)
    seat_number = models.CharField(max_length=10, blank=True)
    presentation_order = models.PositiveIntegerField(
        null=True, blank=True, help_text='Order for stage presentation'
    )

    display_name = models.CharField(
        max_length=255,
        blank=True,
        help_text='Name as shown on the big screen',
    )
    course_name = models.CharField(
        max_length=255,
        blank=True,
        help_text='Optional – course/qualification to display',
    )

    class Meta:
        ordering = ['presentation_order', 'name']

    def __str__(self):
        return f'{self.name} ({self.student_id})'

    def mark_attended(self, staff_initials=None):
        self.attended = True
        self.check_in_time = timezone.now()
        if staff_initials:
            self.checked_in_by = staff_initials
        self.save()

    def get_photo_or_default(self):
        if self.photo:
            return self.photo.url
        return static('ceremony/default_silhouette_grey.png')
    
    def needs_to_return_gown(self):
        """
        Graduates who PURCHASED a gown do NOT return it.
        Graduates who HIRED a gown MUST return it.
        """
        if not self.gown_option:
            return False

        return "hire" in self.gown_option.lower()  # safe match for: Hire ($200)

    
    def save(self, *args, **kwargs):
        # 1) Ensure display_name is set
        if not self.display_name:
            self.display_name = self.name

        # 2) Capture old photo path (if any) BEFORE saving
        old_photo_path = None
        if self.pk:
            try:
                old = Graduate.objects.get(pk=self.pk)
                if old.photo:
                    old_photo_path = old.photo.path
            except Graduate.DoesNotExist:
                pass

        # 3) First save – this writes the NEW upload to disk
        super().save(*args, **kwargs)

        # 4) If there is no current photo
        if not self.photo:
            # and there was an old photo → delete that file
            if old_photo_path and os.path.exists(old_photo_path):
                try:
                    os.remove(old_photo_path)
                except Exception:
                    pass
            return

        # 5) If the photo file didn't actually change, we can skip processing
        current_photo_path = self.photo.path
        if old_photo_path and old_photo_path == current_photo_path:
            # same file name, already processed earlier
            return

        # 6) Process the *current* photo and overwrite original bytes
        try:
            processed = process_photo(current_photo_path)
        except Exception:
            return

        if processed:
            try:
                processed.seek(0)
            except Exception:
                pass
            try:
                with open(current_photo_path, "wb") as f:
                    f.write(processed.read())
            except Exception:
                # If writing fails, don't break the app
                return

        # 7) If there was a different old photo file, delete it
        if old_photo_path and old_photo_path != current_photo_path:
            if os.path.exists(old_photo_path):
                try:
                    os.remove(old_photo_path)
                except Exception:
                    pass


class StageState(models.Model):
    """Simple singleton model to track which graduate is currently on stage."""
    current_graduate = models.ForeignKey(
        Graduate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='current_stage_state',
    )

    def __str__(self):
        return 'Stage State'

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
