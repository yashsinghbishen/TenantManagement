from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible

# from phonenumber_field.modelfields import PhoneNumberField

# Validator for indian phone number formant.
phone_regex = RegexValidator(regex=r'^\+?1?\d{10,13}$',
                             message="""Phone number must
                              be entered in the format: 
                            '+999999999'. Up to 13 digits
                             allowed.""")

# Create your models here.

# Agent Table


class TblAgent(AbstractUser):

    # Validating contact using phone_regex RegexValidator.
    ag_contact = models.CharField(validators=[phone_regex],
                                  null=False, blank=False,
                                  unique=True, max_length=13)
    # Local Address of Agent
    ag_local_address = models.CharField(max_length=255)
    # Permanent Address of Agent
    ag_permanent_address = models.CharField(max_length=255)
    # image of Agent
    ag_profile_image = models.ImageField(upload_to='agents/profiles',
                                         blank=True)

    # Overriding save method to save dafault user
    def agent_save(self, *args, **kwargs):
        self.is_active = False
        self.is_staff = False
        # self.set_password (AbstractUser.password)
        self.is_superuser = False
        super(TblAgent, self).save(*args, **kwargs)

    def verified_save(self, *args, **kwargs):
        self.is_active = True
        self.is_staff = True
        # self.is_superuser = False
        super(TblAgent, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Agent Details'

    def __str__(self):
        return self.username


# Tenant Table
class TblTenant(models.Model):
    # Name of Tenant
    tn_name = models.CharField(null=False, blank=False,
                               max_length=25)
    # Contact of Tenant
    tn_contact = models.CharField(validators=[phone_regex],
                                  null=False, blank=False,
                                  unique=True, max_length=13)
    # Perrmanent Address of tenant
    tn_permanent_address = models.CharField(max_length=255)
    # image of Tenant
    tn_profile = models.ImageField(upload_to='tenant/profiles')
    # Information of tenant's submitted document.
    tn_document_description = models.CharField(null=True,
                                               max_length=255)
    # Copy of documnet
    tn_document = models.ImageField(upload_to='tenant/documents')
    # local reference of tenant
    tn_reference_name = models.CharField(max_length=25)
    # Address of reference
    tn_reference_address = models.CharField(max_length=255)
    # status code: - 1. visit
    # 2.deal Accepted aggrement under process
    # 3.Property handovered 0.Ex-tenant
    tn_status = models.IntegerField(default=1)
    # Agent who allocated the property to tenant
    tn_agent = models.ForeignKey(TblAgent,
                                 on_delete=models.CASCADE)
    # date from when tenant started leaving in property.
    tn_joining_date = models.DateField()
    tn_is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Tenant Datails'

    def __str__(self):
        return self.tn_name


# Master Property Table
class TblMasterProperty(models.Model):
    # Name of property
    msp_name = models.CharField(max_length=30, default='My Property')
    # address of property
    msp_address = models.CharField(null=False,
                                   blank=False, max_length=255)
    # description of property
    msp_description = models.CharField(max_length=255, null=True)
    # Status of allocation of property
    msp_is_allocated = models.BooleanField(default=False)
    msp_is_active = models.BooleanField(default=True)

    #A function to Create new Save
    def new_save(self, *args, **kwargs):
        clone = TblMasterPropertyClone.objects.create(
            cln_alias=self.msp_name+" master clone",
            cln_master=self,
            cln_is_master_clone=True)
        clone.save()
        super(TblMasterProperty, self).save(*args, **kwargs)
    class Meta:
        verbose_name_plural = 'Master Properties'

    def __str__(self):
        return self.msp_address


# Creating master property clone for multiple Allocation
class TblMasterPropertyClone(models.Model):
    # Alias Name for the Clone property
    cln_alias = models.CharField(max_length=30,)
    # Master property Reference
    cln_master = models.ForeignKey(TblMasterProperty, on_delete=models.CASCADE)
    # Check for Master Clone
    cln_is_master_clone = models.BooleanField(default=False)


# Property Table
class TblProperty(models.Model):
    # Master property Clone reference
    pr_master = models.ForeignKey(TblMasterPropertyClone,
                                  on_delete=models.CASCADE)
    # Address of property
    pr_address = models.CharField(max_length=255)
    # Fixed rate of rent of property
    pr_rent = models.DecimalField(decimal_places=2, max_digits=10)
    # Fixed safety deposite for property
    pr_deposite = models.DecimalField(decimal_places=2, max_digits=10)
    #Description for Property
    pr_description = models.CharField(max_length=255,null=True)
    # allocation status of property
    pr_is_allocated = models.BooleanField(default=False)
    pr_is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'All  Properties'

    def __str__(self):
        return self.pr_address


# Visit Table
class TblVisit(models.Model):
    # Tenant reference
    vs_tenant = models.ForeignKey(TblTenant,
                                  on_delete=models.CASCADE)
    # Property reference
    vs_property = models.ForeignKey(TblProperty,
                                    on_delete=models.CASCADE)
    # date of visit
    vs_date = models.DateField()
    # interest of tenant in property after visit
    vs_intrest_status = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = 'Visit Details'

    def __str__(self):
        return self.vs_tenant.tn_name


# Agent Allocation Table
#  @deconstructible
class TblAgentAllocation(models.Model):
    # Agent reference
    al_agent = models.ForeignKey(TblAgent,
                                 on_delete=models.CASCADE)
    # Master property reference
    al_master = models.ForeignKey(TblMasterPropertyClone,
                                  on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Agent Allocation Details'

    def __str__(self):
        return self.al_agent.username


# Rent Collection Table
class TblRentAllocation(models.Model):
    # Property reference
    rc_property = models.ForeignKey(TblProperty,
                                    on_delete=models.CASCADE)
    # identification number on physical copy
    rc_recipt_no = models.IntegerField()
    # month for whixh rent is collected
    rc_month = models.IntegerField(default=1, null=False)
    # year for rent is collected
    rc_year = models.ImageField(max_length=4, null=False)
    # date when the rent is collected
    rc_pay_off_date = models.DateField(null=False)

    class Meta:
        verbose_name_plural = 'Rent Collection Details'

    def __str__(self):
        return self.rc_property.pr_address


# Property Allocation Table
# @deconstructible
class TblPropertyAllocation(models.Model):
    # Property reference
    pa_property = models.ForeignKey(TblProperty,
                                    on_delete=models.CASCADE)
    # Tenant reference
    pa_tenant = models.ForeignKey(TblTenant,
                                  on_delete=models.CASCADE)
    # Starting date of agreement
    pa_agreement_date = models.DateField(null=False)
    # Ending date of Agreement
    pa_agreement_and_date = models.DateField(null=False)
    # Copy of acceptance latter
    pa_acceptance_latter = models.ImageField(
        upload_to='rent/acceptance_latter')
    # Copy of Agreement
    pa_tenancy_agreement = models.ImageField(
        upload_to='rent/tenancy/agreement')
    # Final rent after bargaining
    pa_final_rent = models.FloatField(max_length=10)
    # showing the current allocation status.
    # true for alloted ,false for previous allocation
    pa_is_allocated = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Property Allocation Details'

    def __str__(self):
        return self.pa_property.pr_address



# msp_name yash
# msp_address singh
# msp_description bishen
# msp_have_clones on
# msp_clone_no 5
# msp_clone1 12
# msp_clone2 23
# msp_clone3 34
# msp_clone4 45
# msp_clone5 56


# msp     30
# prp_address0     1
# prp_address7     8
# prp_address9     10
# prp_rent     20.12
# prp_deposite     200
# prp__description     dekha



    # if request.method == "POST":
    #     lst = request.POST
    #     for l in lst.keys():
    #         print(l,"   ",lst[l])
