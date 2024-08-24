from django.contrib.auth.hashers import make_password, check_password
from django.db import models

role = (
    (0, '老师'),
    (1, '学生'),
)


class Teacher(models.Model):
    username = models.CharField(verbose_name='用户名', max_length=50, unique=True)
    phone = models.CharField(max_length=50, verbose_name='手机号', unique=True)
    password = models.CharField(verbose_name='密码', max_length=100)
    email = models.EmailField(null=True, blank=True, unique=True)
    avatar = models.ImageField(upload_to='teacher_images', null=True, blank=True, verbose_name='头像')
    role = models.IntegerField(verbose_name='角色', choices=role, default=0)
    last_login = models.DateTimeField(null=True, blank=True)

    def get_email_field_name(self):
        return 'email'

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "老师"
        verbose_name_plural = "老师"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Class(models.Model):
    name = models.CharField(verbose_name='班级名', max_length=50, unique=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="负责的老师")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "班级"
        verbose_name_plural = "班级"


provinces = (
    (0, '北京市'),
    (1, '天津市'),
    (2, '河北省'),
    (3, '山西省'),
    (4, '内蒙古自治区'),
    (5, '辽宁省'),
    (6, '吉林省'),
    (7, '黑龙江省'),
    (8, '上海市'),
    (9, '江苏省'),
    (10, '浙江省'),
    (11, '安徽省'),
    (12, '福建省'),
    (13, '江西省'),
    (14, '山东省'),
    (15, '河南省'),
    (16, '湖北省'),
    (17, '湖南省'),
    (18, '广东省'),
    (19, '广西壮族自治区'),
    (20, '海南省'),
    (21, '重庆市'),
    (22, '四川省'),
    (23, '贵州省'),
    (24, '云南省'),
    (25, '西藏自治区'),
    (26, '陕西省'),
    (27, '甘肃省'),
    (28, '青海省'),
    (29, '宁夏回族自治区'),
    (30, '新疆维吾尔自治区'),
    (31, '台湾省'),
    (32, '香港特别行政区'),
    (33, '澳门特别行政区')
)


class Student(models.Model):
    student_no = models.CharField(max_length=50, unique=True, verbose_name='学号')
    username = models.CharField(max_length=50, verbose_name='用户名')
    phone = models.CharField(max_length=50, verbose_name='手机号', unique=True)
    password = models.CharField(max_length=100, verbose_name='密码')
    email = models.EmailField(null=True, blank=True, unique=True)
    classs = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students', verbose_name='所在班级')
    avatar = models.ImageField(upload_to='app01/', default='app1/default_avatar.jpg', null=True, blank=True,
                               verbose_name='头像')
    status = models.IntegerField(verbose_name="毕业去向", choices=((0, '就业'), (1, '升学')), default=0)
    role = models.IntegerField(verbose_name='角色', choices=role, default=1)
    province = models.IntegerField(verbose_name='意向地区', choices=provinces, default=16)
    is_read = models.IntegerField(verbose_name="已未读", choices=((0, '未读'), (1, '已读')), default=0)
    last_login = models.DateTimeField(null=True, blank=True)

    def get_email_field_name(self):
        return 'email'

    def __str__(self):
        return self.student_no

    class Meta:
        verbose_name = "学生"
        verbose_name_plural = "学生"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Notice(models.Model):
    title = models.CharField(verbose_name="标题", max_length=200)
    content = models.TextField(verbose_name="内容")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='notices')
    classes = models.ManyToManyField(Class, related_name='notices', verbose_name='班级')
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "通知"
        verbose_name_plural = "通知"



class JobInfo(models.Model):
    # model自增字段
    id = models.AutoField('id', primary_key=True)
    title = models.CharField('岗位名字', max_length=255, default='')
    address = models.CharField('省份', max_length=255, default='')
    type = models.CharField('职业', max_length=255, default='')
    educational = models.CharField('学历', max_length=255, default='')
    workExperience = models.CharField('工作经历', max_length=255, default='')
    workTag = models.CharField('工作标签', max_length=2555, default='')
    salary = models.CharField('薪资', max_length=255, default='')
    salaryMonth = models.CharField('年终奖', max_length=255, default='')
    companyTags = models.CharField('公司福利', max_length=2555, default='')
    hrWork = models.CharField('人事职位', max_length=255, default='')
    hrName = models.CharField('人事名字', max_length=255, default='')
    pratice = models.BooleanField('是否为实习单位', max_length=255, default='')
    companyTitle = models.CharField('公司名称', max_length=255, default='')
    companyAvatar = models.CharField('公司头像', max_length=255, default='')
    companyNature = models.CharField('公司性质', max_length=255, default='')
    companyStatus = models.CharField('公司状态', max_length=255, default='')
    companyPeople = models.CharField('公司人数', max_length=255, default='')
    detailUrl = models.CharField('详情地址', max_length=2555, default='')
    companyUrl = models.CharField('公司详情地址', max_length=2555, default='')
    createTime = models.DateField('创建时间', auto_now_add=True)
    dist = models.CharField('行政区', max_length=255, default='')

    def toDict(self):
        return {'title': self.title, 'address': self.address, 'type': self.type, 'educational': self.educational,
                'workExperience': self.workExperience, 'workTag': self.workTag, 'salary': self.salary,
                'salaryMonth': self.salaryMonth, 'companyTags': self.companyTags,'hrName': self.hrName.strip(self.hrWork),
                'hrWork': self.hrWork, 'pratice': self.pratice,'companyTitle': self.companyTitle,
                'companyAvatar': self.companyAvatar,'companyNature': self.companyNature, 'companyStatus': self.companyStatus,
                'companyPeople': self.companyPeople,'detailUrl':self.detailUrl,'companyUrl':self.companyUrl,
                'dist':self.dist}

    # 数据库的表名称
    class Meta:
        verbose_name = "招聘信息"
        verbose_name_plural = "招聘信息"


class School(models.Model):
    name = models.CharField(verbose_name="院校名称", max_length=32, null=True)
    location = models.CharField(verbose_name="所在地", max_length=32, null=True)
    department = models.CharField(verbose_name="院校隶属", max_length=32, null=True)
    department_choices = (

        (1, "研究生院"),
        (0, " ")
    )
    is_research = models.BooleanField(verbose_name="是否有研究生院", choices=department_choices, max_length=32,
                                      null=True)
    line_choices = (

        (1, "自划线"),
        (0, " ")
    )
    is_auto_line = models.BooleanField(verbose_name="是否为自划线院校", choices=line_choices, max_length=32, null=True)
    double_choices = (
        (1, "双一流"),
        (0, " ")
    )
    is_double_one = models.BooleanField(verbose_name="是否为双一流院校", choices=double_choices, max_length=32,
                                        null=True)
    icon = models.CharField(verbose_name="图标链接", max_length=255, default='')
    url = models.CharField(verbose_name="院校链接", max_length=255, default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "院校"
        verbose_name_plural = verbose_name

