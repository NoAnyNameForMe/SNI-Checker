
# SNI Checker

با تشکر از تمام دوستانی که زحمت کشیدند برای اینترنت آزاد.

ممنون از سگارو، وحید و IRCF

چون برای خودم خیلی سخت بود تک تک دامنه ها رو چک کنم و لیست طولانی هم داره

این کد مبتدی کوچیک رو نوشتم اینکه پیدا کردن SNI راحت تر باشه متناسب با اینترنت شما، به جای اینکه تک تک دستی چک کنیم.

من کاملا مبتدی هستنم، و قطعا این کد حرفه ای نیست و یکم کار راه انداز هستش. شرمنده


## [ورژن 1.3](https://github.com/NoAnyNameForMe/SNI-Checker/releases/tag/V1.3)

به دلیل اینکه در قسمت Speed Test یک سری مشکلات برای تعدادی وجود داشت و برای تعدادی خیر، این قسمت فعلا در کد حذف میشود.

به زودی قسمت Speed Test را با کانفیگ Reality، منتشر میکنم که کانفیگ را با SNI های چک شده تست بگیرد.

- در فایل خروجی مربوط به دامنه های سالم که پینگ دارید، در قسمت Successful Domains، فقط دامنه هایی که TLSv1.3 بودند و پینگ داشتید نمایش داده میشه

فایل خروجی: Domain Result.txt

- اضافه شدن Speed Test بعد از پروسه پیدا کردن دامنه سالم، از شما سوال میپرسه که اسپید تست را میخواهید انجام بدید یا خیر

که با موافقت، از دامنه های سالمی که پینگ داشنید و TLSv1.3 داشتند اسپید تست گرفته میشه که سرعت دانلود و آپلود سرور شما به اون دامنه چقدر هستش و در فایل خروچی جداگانه سیو میشه و مقدار حجم دانلود و آپلود برای این پروسه هم آخر به شما نمایش میده.

( فقط اینچا مواظب مصرف دانلود و آپلود باشید، هرچی تعداد دامنه های سالم بیشتر باشه مصرف شما هم به همون نسبت بالا خواهد بود.)

فایل خروجی: Speed Test Result.txt

## راه اندازی
پیشناز هایی که باید نصب کنید
```bash
pip install requests
pip install ping3
pip install prettytable
pip install tqdm
pip install speedtest_cli
```
کافیه از داخل سایت bgp.tools، لیست مورد نظرتون رو به صورت یک جا کپی کنید، به عنوان مثال

آموزش استفاده از سایت bgp.tools

https://telegra.ph/آموزش-یافتن-SNI-برای-استفاده-با-رئالیتی-05-11
```bash
A	DNS
37.59.0.8	www.dylemo.pl, dylemo.pl
37.59.0.18	www.kisland.com, kisland.com
37.59.0.116	stage.mozilla-hispano.org, foroestatico.mozilla-hispano.org ( 5 more...)
37.59.0.183	shinken.2le.net
.
.
.
.
```

وقتی که کلا دیتا رو کپی کردید، داخل یک فایل txt سیو کنید.

نمونه ای که من کپی کردم

![246831248-65fd6fcf-5ad2-4968-be78-26a7e277a8d2](https://github.com/NoAnyNameForMe/SNI-Checker/assets/137012307/35e0af12-5a2e-49bd-a33c-d4c6f8eb2afc)

بعد کد رو ران کنید، از شما مسیر فایل txt میپرسه که کامل وارد کنید. به عنوان مثال

```bash
C:\SNI\domains.txt
```
بعد خود کد میاد دامنه ها رو جدا میکنه و اضافه هایی که مربوط به دامنه نمیشه رو حذف میکنه و شروع میکنه به پینگ گرفتن از دامنه ها.

## نتیجه

مربوط به Domain Result.txt

![domain result](https://github.com/NoAnyNameForMe/SNI-Checker/assets/137012307/0b83024c-e938-4362-b0f7-63068b52fa3c)

مربوط به اسپید تست Speed Test Result.txt

![speed test result](https://github.com/NoAnyNameForMe/SNI-Checker/assets/137012307/839cde27-74eb-42f2-b682-6783c9b0d148)

![speed test result 1](https://github.com/NoAnyNameForMe/SNI-Checker/assets/137012307/ca9a3ffc-37f1-4879-a51b-2a4b2087bc92)
