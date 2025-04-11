from django.contrib import admin
from .models import LoanCalculation, RepaymentSchedule, Fee, ApplicationFee


class RepaymentScheduleInline(admin.TabularInline):
    model = RepaymentSchedule
    extra = 0
    fields = ('payment_number', 'payment_date', 'payment_amount', 'principal_amount', 'interest_amount', 'remaining_balance')
    readonly_fields = fields
    can_delete = False
    max_num = 0
    show_change_link = False


@admin.register(LoanCalculation)
class LoanCalculationAdmin(admin.ModelAdmin):
    list_display = ('id', 'application', 'interest_type', 'interest_rate', 'loan_amount', 'loan_term_years', 'monthly_payment')
    list_filter = ('interest_type', 'compounding_period')
    search_fields = ('application__id', 'application__borrower__first_name', 'application__borrower__last_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [RepaymentScheduleInline]


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'fee_type', 'calculation_method', 'amount', 'is_active')
    list_filter = ('fee_type', 'calculation_method', 'is_active')
    search_fields = ('name', 'description')
    filter_horizontal = ('products',)


@admin.register(ApplicationFee)
class ApplicationFeeAdmin(admin.ModelAdmin):
    list_display = ('application', 'fee', 'calculated_amount', 'is_waived')
    list_filter = ('fee__fee_type', 'is_waived')
    search_fields = ('application__id', 'fee__name')
    readonly_fields = ('created_at', 'updated_at')
