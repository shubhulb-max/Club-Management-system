from django.conf import settings
from django.db import models
from datetime import date, timedelta
from calendar import monthrange
from accounts.phone_utils import normalize_phone_number


class Player(models.Model):
    MEMBERSHIP_LAPSE_DAYS = 30
    MEMBERSHIP_LEFT_DAYS = 90

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )

    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    age = models.PositiveIntegerField(default=0)

    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    phone_number = models.CharField(max_length=15,unique=True, null=True, blank=True)

    ROLE_CHOICES = [
        ("top_order_batter", "Top-order batter"),
        ("middle_order_batter", "Middle-order batter"),
        ("wicket_keeper_batter", "Wicket-keeper batter"),
        ("wicket_keeper", "Wicket-keeper"),
        ("bowler", "Bowler"),
        ("all_rounder", "All-Rounder"),
        ("lower_order_batter", "Lower-order batter"),
        ("opening_batter", "Opening batter"),
        ("none", "None"),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="all_rounder")

    @property
    def membership_active(self):
        """
        A player's membership is active if they have no unpaid 'Monthly Fee'
        invoices older than 30 days.
        """
        thirty_days_ago = date.today() - timedelta(days=self.MEMBERSHIP_LAPSE_DAYS)
        return not self.transactions.filter(
            category='monthly',
            paid=False,
            due_date__lt=thirty_days_ago
        ).exists()

    def oldest_unpaid_monthly_due_date(self):
        overdue_transaction = (
            self.transactions.filter(category="monthly", paid=False)
            .order_by("due_date", "id")
            .first()
        )
        return overdue_transaction.due_date if overdue_transaction else None

    def computed_membership_status(self, as_of=None):
        membership = getattr(self, "membership", None)
        if membership is None:
            return None
        if membership.status == Membership.STATUS_PENDING:
            return Membership.STATUS_PENDING
        if membership.fee_exempt:
            return Membership.STATUS_ACTIVE

        as_of = as_of or date.today()
        oldest_due_date = self.oldest_unpaid_monthly_due_date()
        if not oldest_due_date:
            return Membership.STATUS_ACTIVE

        left_cutoff = as_of - timedelta(days=self.MEMBERSHIP_LEFT_DAYS)
        lapse_cutoff = as_of - timedelta(days=self.MEMBERSHIP_LAPSE_DAYS)
        if oldest_due_date < left_cutoff:
            return Membership.STATUS_LEFT
        if oldest_due_date < lapse_cutoff:
            return Membership.STATUS_INACTIVE
        return Membership.STATUS_ACTIVE

    def sync_membership_status(self, as_of=None, *, save=True):
        membership = getattr(self, "membership", None)
        if membership is None:
            return None

        computed_status = self.computed_membership_status(as_of=as_of)
        if computed_status and membership.status != computed_status:
            membership.status = computed_status
            if save:
                membership.save(update_fields=["status"])
        return membership.status


    def save(self, *args, **kwargs):
        if self.user:
            if not self.first_name:
                self.first_name = self.user.first_name
            if not self.last_name:
                self.last_name = self.user.last_name
            if not self.phone_number:
                self.phone_number = self.user.phone_number

        if self.phone_number:
            self.phone_number = normalize_phone_number(self.phone_number)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Membership(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_PENDING = "pending"
    STATUS_LEFT = "left"

    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    join_date = models.DateField()
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_LEFT, 'Left Club'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    fee_exempt = models.BooleanField(default=False)
    fee_exempt_reason = models.CharField(max_length=255, blank=True)

    def month_bounds(self, billing_date):
        month_start = billing_date.replace(day=1)
        month_end = billing_date.replace(day=monthrange(billing_date.year, billing_date.month)[1])
        return month_start, month_end

    def is_on_leave_for_month(self, billing_date):
        month_start, month_end = self.month_bounds(billing_date)
        return self.leave_periods.filter(
            start_date__lte=month_end,
            end_date__gte=month_start,
        ).exists()

    def __str__(self):
        return f"{self.player}'s Membership"


class MembershipLeave(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name="leave_periods")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-start_date", "-id"]

    def __str__(self):
        return f"{self.membership.player} leave {self.start_date} to {self.end_date}"

class Subscription(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=750.00)
    start_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.player}'s Subscription"


class RegistrationRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password_hash = models.CharField(max_length=128)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_registration_requests",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.phone_number = normalize_phone_number(self.phone_number)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.phone_number} ({self.status})"
