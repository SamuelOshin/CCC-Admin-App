

from django.db import models
from multiselectfield import MultiSelectField



class ClergyDetails(models.Model):
    clergy_id = models.AutoField(primary_key=True)
    profile_picture = models.ImageField(upload_to='parish_pic', default='parish_pic/Celestial-Church-of-Christ-CCC.jpg')
    reg_number = models.IntegerField()
    trg_number = models.IntegerField()
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    alias = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('', 'Select one'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('undefined', 'None'),
    ], default='') # Assuming 'male', 'female', 'other'
    marital_status = models.CharField(max_length=20,choices=[
         ('', 'Select one'),
         ('Single', 'Single'),
        ('Married', 'Married'),
        ('Single Parent', 'Single Parent'),
        ('Divorced', 'Divorced'),
        ('Widow', 'Widow'),
    ], default='' )  # Assuming possible values
    dob = models.DateField()
    spoken_languages = MultiSelectField(choices=[
        ('English', 'English'),
        ('French', 'French'),
        ('Yoruba', 'Yoruba'),
        ('Igbo', 'Igbo'),
        ('Hausa', 'Hausa'),
        ('French', 'French'),
        ('Egun', 'Egun'),
        ('Dutch', 'Dutch'),
        ('Pidgin', 'Pidgin'),
        ('Arabic', 'Arabic'),
    ], max_length=100)
    place_of_birth = models.CharField(max_length=100)
    
    nationality = models.CharField(max_length=50, choices=[
        ('Nigeria', 'Nigeria'),
        ('Ghana', 'Ghana'),
        ('Benin Republic', 'Benin Republic'),
        ('Togo', 'Togo'),
        ('Cameroon', 'Cameroon'),
        ('Ivory Coast', 'Ivory Coast'),
        ('Liberia', 'Liberia'),
        ('Sierra Leone', 'Sierra Leone'),
        ('Guinea', 'Guinea'),
        ('Guinea Bissau', 'Guinea Bissau'),
        ('Senegal', 'Senegal'),
        ('Mali', 'Mali'),
        ('Burkina Faso', 'Burkina Faso'),
        ('Niger', 'Niger'),
        ('Chad', 'Chad'),
        ('Central African Republic', 'Central African Republic'),
        ('Sudan', 'Sudan'),
        ('South Sudan', 'South Sudan'),
        ('Ethiopia', 'Ethiopia'),
        ('Eritrea', 'Eritrea'),
        ('Somalia', 'Somalia'),
        ('Djibouti', 'Djibouti'),
        ('Kenya', 'Kenya'),
        ('Uganda', 'Uganda'),
        ('Rwanda', 'Rwanda'),
        ('Burundi', 'Burundi'),
        ('Tanzania', 'Tanzania'),
        ('Zambia', 'Zambia'),
        ('Malawi', 'Malawi'),
        ('Mozambique', 'Mozambique'),
        ('Zimbabwe', 'Zimbabwe'),
        ('Angola', 'Angola'),
        ('Namibia', 'Namibia'),
        ('Botswana', 'Botswana'),
        ('South Africa', 'South Africa'),
        ('Lesotho', 'Lesotho'),
        ('Swaziland', 'Swaziland'),
        ('Madagascar', 'Madagascar'),
        ('Mauritius', 'Mauritius'),
        ('Seychelles', 'Seychelles'),
        ('Comoros', 'Comoros'),
        ('Mauritania', 'Mauritania'),
        ('Western Sahara', 'Western Sahara'),
        ('Morocco', 'Morocco'),
        ('Algeria', 'Algeria'),
        ('Tunisia', 'Tunisia'),
        ('Libya', 'Libya'),
        ('Egypt', 'Egypt'),
        ('Gambia', 'Gambia'),
        ('Greece', 'Greece'),
        ('Italy', 'Italy'),
        ('Spain', 'Spain'),
        ('Portugal', 'Portugal'),
        ('France', 'France'),
        ('Germany', 'Germany'),
        ('Belgium', 'Belgium'),
        ('Netherlands', 'Netherlands'),
        ('Luxembourg', 'Luxembourg'),
        ('Switzerland', 'Switzerland'),
        ('Austria', 'Austria'),
        ('Czech Republic', 'Czech Republic'),
        ('Slovakia', 'Slovakia'),
        ('Hungary', 'Hungary'),
        ('Slovenia', 'Slovenia'),
        ('Croatia', 'Croatia'),
        ('Bosnia and Herzegovina', 'Bosnia and Herzegovina'),
        ('Serbia', 'Serbia'),
        ('Montenegro', 'Montenegro'),
        ('Albania', 'Albania'),
        ('Macedonia', 'Macedonia'),
        ('Bulgaria', 'Bulgaria'),
        ('Romania', 'Romania'),
        ('Moldova', 'Moldova'),
        ('Ukraine', 'Ukraine'),
        ('Belarus', 'Belarus'),
        ('Poland', 'Poland'),
        ('Lithuania', 'Lithuania'),
        ('Latvia', 'Latvia'),
        ('Estonia', 'Estonia'),
        ('Finland', 'Finland'),
        ('Sweden', 'Sweden'),
        ('Norway', 'Norway'),
        ('Denmark', 'Denmark'),
        ('Iceland', 'Iceland'),
        ('Ireland', 'Ireland'),
        ('United Kingdom', 'United Kingdom'),
        ('Canada', 'Canada'),
        ('United States', 'United States'),
        ('Mexico', 'Mexico'),
        ('Greenland', 'Greenland'),
        ('Cuba', 'Cuba'),
        ('Haiti', 'Haiti'),
        ('Dominican Republic', 'Dominican Republic'),
        ('Guatemala', 'Guatemala'),
        ('Belize', 'Belize'),
        ('El Salvador', 'El Salvador'),
        ('Honduras', 'Honduras'),
        ('Nicaragua', 'Nicaragua'),
        ('Costa Rica', 'Costa Rica'),
        ('Panama', 'Panama'),
        ('Colombia', 'Colombia'),
                ('Venezuela', 'Venezuela'),
                ('Peru', 'Peru'),
            ], error_messages={'required': 'Please select a country.'})
    state_of_origin = models.CharField(max_length=50, error_messages={'required': 'Please enter the state of origin.'})
    lga_if_nigerian = models.CharField(max_length=50, error_messages={'required': 'Please enter the LGA if Nigerian.'})
    blood_group = models.CharField(max_length=5, choices=[
        ('', 'Select one'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ], default='', blank=True, error_messages={'required': 'Please select a blood group.'})
    genotype = models.CharField(max_length=5, choices=[
        ('', 'Select one'),
        ('AA', 'AA'),
        ('AS', 'AS'),
        ('SS', 'SS'),
        ('SC', 'SC'),
        ('AC', 'AC'),
        ('CC', 'CC'),
    ], default='', error_messages={'required': 'Please select a genotype.'})
    any_ailment = models.CharField(max_length=3, choices=[
        ('', 'Select one'),
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], default='',  error_messages={'required': 'Please select an option.'})
    any_disabilities = models.CharField(max_length=3, choices=[
        ('', 'Select one'),
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], default='', error_messages={'required': 'Please select an option.'})
    ailment = models.CharField(max_length=50, null=True, blank=True, error_messages={'required': 'Please enter the ailment.'})
    disability = models.CharField(max_length=50, null=True, blank=True, error_messages={'required': 'Please enter the disability.'})
    permanent_address = models.CharField(max_length=255, error_messages={'required': 'Please enter the permanent address.'})
    resident_address = models.CharField(max_length=255, error_messages={'required': 'Please enter the resident address.'})
    parish = models.CharField(max_length=100, error_messages={'required': 'Please enter the parish.'})
    parish_address = models.CharField(max_length=255, error_messages={'required': 'Please enter the parish address.'})
    telephone = models.CharField(max_length=20, error_messages={'required': 'Please enter the telephone number.'})
    email_address = models.EmailField(max_length=255, error_messages={'required': 'Please enter the email address.'})
    former_religion = models.CharField(max_length=50, null=True, blank=True, error_messages={'required': 'Please enter the former religion.'})
    denomination = models.CharField(max_length=50, null=True, blank=True, error_messages={'required': 'Please enter the denomination.'})
    status_former_religion = models.CharField(max_length=255, null=True, blank=True, error_messages={'required': 'Please enter the status of former religion.'})
    entry_date_in_ccc = models.DateField(error_messages={'required': 'Please enter the entry date in CCC.'})
    first_parish = models.CharField(max_length=255, error_messages={'required': 'Please enter the first parish.'})
    shepherd_who_baptized_you = models.CharField(max_length=255, error_messages={'required': 'Please enter the shepherd who baptized you.'})
    shepherd_who_sanctified_you = models.CharField(max_length=255, error_messages={'required': 'Please enter the shepherd who sanctified you.'})
    date_when_baptized = models.DateField(error_messages={'required': 'Please enter the date when baptized.'})
    parish_where_baptized = models.CharField(max_length=255, error_messages={'required': 'Please enter the parish where baptized.'})
    first_annointment = models.CharField(max_length=50, choices=[
            ('MALE RANK', (
            ('', '--select--'),
            ('Asst. Elder Bro', 'Asst. Elder Bro'),
            ('Full. Elder Bro', 'Full. Elder Bro'),
            ('Cape Elde Bro', 'Cape Elde Bro'),
            ('Lace Elder Bro', 'Lace Elder Bro'),
            ('Snr Elder Bro', 'Snr Elder Bro'),
            ('Sup. Snr. Elder Brp', 'Sup. Snr. Elder Brp'),
            ('Asst. Leader', 'Asst. Leader'),
            ('Full Leader', 'Full Leader'),
            ('Senior Leader', 'Senior Leader'),
            ('Superior Leader', 'Superior Leader'),
            ('Superior Snr. Leader', 'Superior Snr. Leader'),
            ('Asst. Evangelist', 'Asst. Evangelist'),
            ('Full Evngelist', 'Full Evngelist'),
            ('Senior Evang', 'Senior Evang'),
            ('Most Snr. Evangelist', 'Most Snr. Evangelist'),
            ('Ven. Snr. Evang', 'Ven. Snr. Evang'),
            ('Asst. Sup Evangelist', 'Asst. Sup Evangelist'),
            ('Ven. Sup Evang', 'Ven. Sup Evang'),
            ('Asst. Most Sup Evang', 'Asst. Most Sup Evang'),
            ('Most Sup Evang', 'Most Sup Evang'),
        )),
        ('PROPHETS', (
            ('One Cross Prophet', 'One Cross Prophet'),
            ('Cape Prophet', 'Cape Prophet'),
            ('Lace Prophet', 'Lace Prophet'),
            ('Snr Prophet(Wolider)', 'Snr Prophet(Wolider)'),
            ('Sup Prophet(Wolider)', 'Sup Prophet(Wolider)'),
            ('Sup. Snr Prophet(Wolider)', 'Sup. Snr Prophet(Wolider)'),
        )),
        ('FEMALE RANK', (
            ('Asst. Elder Sister', 'Asst. Elder Sister'),
            ('Elder Sister', 'Elder Sister'),
            ('Cape Elder Sister', 'Cape Elder Sister'),
            ('Lace Elder Sister', 'Lace Elder Sister'),
            ('Snr Elder Sister', 'Snr Elder Sister'),
            ('Sup. Snr Elder Sister', 'Sup. Snr Elder Sister'),
            ('lace Sup Elder Sister', 'lace Sup Elder Sister'),
            ('Lace Sup. Snr Elder Sister', 'Lace Sup. Snr Elder Sister'),
            ('Mother Celestial', 'Mother Celestial'),
        )),
        ('PROPHETESS', (
            ('One Cross Prophetess', 'One Cross Prophetess'),
            ('Cape Prophetess', 'Cape Prophetess'),
            ('Lace Prophetess', 'Lace Prophetess'),
            ('Snr Prophetess(Wolima)', 'Snr Prophetess(Wolima)'),
            ('Sup Prophetess(Wolima)', 'Sup Prophetess(Wolima)'),
            ('Sup. Snr. Prophetess(Wolima)', 'Sup. Snr. Prophetess(Wolima)'),
        )),
    ], error_messages={'required': 'Please select the first annointment.'})
    date_of_first_annointment = models.DateField(error_messages={'required': 'Please enter the date of first annointment.'})
    present_annointment = models.CharField(max_length=50, choices = [
            ('MALE RANK', (
            ('', '--select--'),
            ('Asst. Elder Bro', 'Asst. Elder Bro'),
            ('Full. Elder Bro', 'Full. Elder Bro'),
            ('Cape Elde Bro', 'Cape Elde Bro'),
            ('Lace Elder Bro', 'Lace Elder Bro'),
            ('Snr Elder Bro', 'Snr Elder Bro'),
            ('Sup. Snr. Elder Bro', 'Sup. Snr. Elder Bro'),
            ('Asst. Leader', 'Asst. Leader'),
            ('Full Leader', 'Full Leader'),
            ('Senior Leader', 'Senior Leader'),
            ('Superior Leader', 'Superior Leader'),
            ('Superior Snr. Leader', 'Superior Snr. Leader'),
            ('Asst. Evangelist', 'Asst. Evangelist'),
            ('Full Evangelist', 'Full Evngelist'),
            ('Senior Evang', 'Senior Evang'),
            ('Most Snr. Evangelist', 'Most Snr. Evangelist'),
            ('Ven. Snr. Evang', 'Ven. Snr. Evang'),
            ('Asst. Sup Evangelist', 'Asst. Sup Evangelist'),
            ('Ven. Sup Evang', 'Ven. Sup Evang'),
            ('Asst. Most Sup Evang', 'Asst. Most Sup Evang'),
            ('Most Sup Evang', 'Most Sup Evang'),
        )),
        ('PROPHETS', (
            ('One Cross Prophet', 'One Cross Prophet'),
            ('Cape Prophet', 'Cape Prophet'),
            ('Lace Prophet', 'Lace Prophet'),
            ('Snr Prophet(Wolider)', 'Snr Prophet(Wolider)'),
            ('Sup Prophet(Wolider)', 'Sup Prophet(Wolider)'),
            ('Sup. Snr Prophet(Wolider)', 'Sup. Snr Prophet(Wolider)'),
        )),
        ('FEMALE RANK', (
            ('Asst. Elder Sister', 'Asst. Elder Sister'),
            ('Elder Sister', 'Elder Sister'),
            ('Cape Elder Sister', 'Cape Elder Sister'),
            ('Lace Elder Sister', 'Lace Elder Sister'),
            ('Snr Elder Sister', 'Snr Elder Sister'),
            ('Sup. Snr Elder Sister', 'Sup. Snr Elder Sister'),
            ('lace Sup Elder Sister', 'lace Sup Elder Sister'),
            ('Lace Sup. Snr Elder Sister', 'Lace Sup. Snr Elder Sister'),
            ('Mother Celestial', 'Mother Celestial'),
        )),
        ('PROPHETESS', (
            ('One Cross Prophetess', 'One Cross Prophetess'),
            ('Cape Prophetess', 'Cape Prophetess'),
            ('Lace Prophetess', 'Lace Prophetess'),
            ('Snr Prophetess(Wolima)', 'Snr Prophetess(Wolima)'),
            ('Sup Prophetess(Wolima)', 'Sup Prophetess(Wolima)'),
            ('Sup. Snr. Prophetess(Wolima)', 'Sup. Snr. Prophetess(Wolima)'),
        )),
    ], error_messages={'required': 'Please select the present annointment.'})
    date_of_present_annointment = models.DateField(null=True, blank=True, error_messages={'required': 'Please enter the date of present annointment.'})
    edu_level = MultiSelectField(choices=[
        ('NONE','None'),  # Used for non-educated members
        ('Primary', 'Primary'),
        ('Secondary', 'Secondary'),
        ('College', 'College'),
        ('Polytechnic', 'Polytechnic'),
        ('University', 'University'),
        ('Modern', 'Modern'),
    ], max_length=250, error_messages={'required': 'Please select the education level.'})
    edu_qualification = MultiSelectField(choices=[
        ('NONE', 'None'),  # Used for non-educated members
        ('Primary Leaving Certificate', 'Primary Leaving Certificate'),
        ('First School Leaving Certificate', 'First School Leaving Certificate'),
        ('Junior Secondary School Certificate', 'Junior Secondary School Certificate'),
        ('Senior Secondary School Certificate', 'Senior Secondary School Certificate'),
        ('National Certificate of Education', 'National Certificate of Education'),
        ('National Diploma', 'National Diploma'),
        ('Higher National Diploma', 'Higher National Diploma'),
        ('Bachelor of Arts', 'Bachelor of Arts'),
        ('Bachelor of Science', 'Bachelor of Science'),
        ('Bachelor of Technology', 'Bachelor of Technology'),
        ('Bachelor of Engineering', 'Bachelor of Engineering'),
        ('Bachelor of Education', 'Bachelor of Education'),
        ('Bachelor of Laws', 'Bachelor of Laws'),
        ('Bachelor of Medicine', 'Bachelor of Medicine'),
        ('Bachelor of Surgery', 'Bachelor of Surgery'),
        ('Master of Arts', 'Master of Arts'),
        ('Master of Science', 'Master of Science'),
        ('Master of Technology', 'Master of Technology'),
        ('Master of Engineering', 'Master of Engineering'),
        ('Master of Education', 'Master of Education'),
        ('Master of Laws', 'Master of Laws'),
        ('Master of Medicine', 'Master of Medicine'),
        ('Master of Surgery', 'Master of Surgery'),
        ('Doctor of Philosophy', 'Doctor of Philosophy'),
        ('Doctor of Medicine', 'Doctor of Medicine'),
        ('Doctor of Surgery', 'Doctor of Surgery'),
        ('Doctor of Laws', 'Doctor of Laws'),
    ], max_length=1000, error_messages={'required': 'Please select the education qualification.'})
        
    apprenticeship = models.CharField(max_length=255, error_messages={'required': 'Please enter the apprenticeship.'})
    hobbies = models.CharField(max_length=255, error_messages={'required': 'Please enter the hobbies.'})
    area_of_calling = MultiSelectField(choices=[
        
        ('Evangelism', 'Evangelism'),
        ('Shepherdship', 'Shepherdship'),
        ('Prophecy', 'Prophecy'),
        ('Teacher', 'Teacher'),
        ('Church Planting', 'church Planting'),
        ('Church Addministation', 'Church Administration'),
        ('Prayer Warroir', 'Prayer Warrior'),
        ('Choir Ministry', 'Choir Ministry'),
        ('Marriage Counselling', 'Marriage Counselling'),
        ('Youth Work', "Youth Work"),
        ('Women\'s Ministrations', 'Women\'s Ministrations'),
        ('Others', 'Others'),

    ], max_length=250, error_messages={'required': 'Please select the area of calling.'})
    working_experience_option = models.CharField(max_length=3, choices=[
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], error_messages={'required': 'Please select an option.'})  # Assuming 'Yes', 'No'
    work_experience_ifyes = models.CharField(max_length=255, null=True, blank=True, error_messages={'required': 'Please enter the work experience if yes.'})
    spouse = models.CharField(max_length=100, error_messages={'required': 'Please enter the spouse.'})
    father = models.CharField(max_length=100, error_messages={'required': 'Please enter the father.'})
    mother = models.CharField(max_length=100, error_messages={'required': 'Please enter the mother.'})
    next_of_kin = models.CharField(max_length=50, error_messages={'required': 'Please enter the next of kin.'})
    relation_in_ccc = models.CharField(max_length=255, error_messages={'required': 'Please enter the relation in CCC.'})
    children_info = models.CharField(max_length=255, error_messages={'required': 'Please enter the children info.'})

    class Meta:
        db_table = 'clergydetails'

    def __str__(self):
        return self.first_name + " " + self.last_name
