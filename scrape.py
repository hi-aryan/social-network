# pip installed selenium beautifulsoup4
# it said this after "pip install selenium beautifulsoup4": 
# "
# Installing collected packages: sortedcontainers, websocket-client, urllib3, soupsieve, sniffio, pysocks, pycparser, h11, certifi, attrs, wsproto, outcome, cffi, beautifulsoup4, trio, trio-websocket, selenium
# Successfully installed attrs-25.3.0 beautifulsoup4-4.13.4 certifi-2025.8.3 cffi-1.17.1 h11-0.16.0 outcome-1.3.0.post0 pycparser-2.22 pysocks-1.7.1 selenium-4.35.0 sniffio-1.3.1 sortedcontainers-2.4.0 soupsieve-2.7 trio-0.30.0 trio-websocket-0.12.2 urllib3-2.5.0 websocket-client-1.8.0 wsproto-1.2.0
# "
# ^ not added to requirements.txt !

from selenium import webdriver
from bs4 import BeautifulSoup
import time

driver = webdriver.Chrome()
#driver.get("https://www.kth.se/student/kurser/program/TCOMK/20252/arskurs1?l=en")
# driver.get("https://www.kth.se/student/kurser/program/CTKEM/20252/arskurs1?l=en")
driver.get("https://www.kth.se/student/kurser/program/CDATE/20252/arskurs1?l=en")

time.sleep(5)

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
#print(soup.prettify())
driver.quit()

table = soup.find("table")
print(table)

for row in soup.find_all("tr"):
    cols = row.find_all("td")
    if len(cols) >= 1:
        text = cols[0].get_text(strip=True)
        parts = text.split(" ", 1)
        if len(parts) == 2:
            course_code = parts[0]
            course_name = parts[1][:200] # Clip to 200 chars just in case
            print("\ncourse code:", course_code, "\ncourse name:", course_name)



print("\n\n\n")



import re

title = (soup.title.string or "").strip()


# 2) Extract *all* codes in parentheses, take the *last* one
codes = re.findall(r"\(([A-Z0-9]+)\)", title)
programme_code = codes[-1] if codes else None


# 3) Cut off everything *after* that "(CODE)"
before = title.split(f"({programme_code})", 1)[0]


# 4) If there’s a comma, assume the *last* clause is the programme phrase
raw_prog = before.rsplit(",", 1)[-1].strip()


# 5) Strip any “—Programme in” prefix (Degree/Master’s/Bachelor’s etc.)
programme_name = re.sub(
    r"^(?:.*Programme(?:\s+in)?\s+)",
    "",
    raw_prog,
    flags=re.IGNORECASE
).strip()


print("programme code:", programme_code)
print("programme name:", programme_name)



# add and commit program and courses

from flasknetwork import create_app, db
from flasknetwork.models import Course_Program, Program, Course

app = create_app()
app.app_context().push()

program = Program.query.filter_by(code=programme_code).first()
if not program:
    while True:
        ptype = input(f"Enter type for “{programme_name}” [{programme_code}] (bachelor/master): ").strip().lower()
        if ptype in ("bachelor", "master"):
            break
        print("  ✗ Invalid—must be 'bachelor' or 'master'")
    # 3) create & commit
    program = Program(
        name=programme_name,
        code=programme_code,
        program_type=ptype
    )
    db.session.add(program)
    db.session.commit()
    print(f"✓ Created Program {programme_code} ({programme_name}) as {ptype}")
else:
    print(f"→ Program {programme_code} already exists ({program.program_type})")


for row in soup.find_all("tr"):
    cols = row.find_all("td")
    if len(cols) < 1:
        continue

    text = cols[0].get_text(strip=True)
    parts = text.split(" ", 1)
    if len(parts) != 2:
        continue

    course_code, course_name = parts

    # 1) Upsert course
    course = Course.query.filter_by(code=course_code).first()
    if not course:
        course = Course(name=course_name, code=course_code)
        db.session.add(course)
        db.session.commit()
        print(f"✓ Created Course {course_code} ({course_name})")
    else:
        print(f"→ Course {course_code} already exists")

    existing_link = Course_Program.query.filter_by(
        course_id=course.id, 
        program_id=program.id
    ).first()
    if not existing_link:
        #program.courses.append(course)
        cp = Course_Program(course=course, program=program)
        db.session.add(cp)
        db.session.commit()
        print(f"→ Linked {course_code} to Program {programme_code}")
    else:
        print(f"→ {course_code} already linked to Program {programme_code}")