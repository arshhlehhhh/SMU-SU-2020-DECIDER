import inflect

grades_dict = {"A+":4.3, "A":4.0, "A-":3.7, "B+":3.3, "B":3.0, "B-":2.7, "C+":2.3, "C":2.0, "C-":1.7, "D+":1.3, "D":1.0, "F":0.0}

def check_grade_input(grade):
    if grade[0] not in ["A", "B", "C", "D", "E","F","U","P"]:
        return False
    if len(grade) > 1:
        if grade[-1] not in ["-", "+"]:
            return False
    return True

def check_cu(cu):
    try:
        if (float(cu) % 0.5 != 0) and (float(cu) < 0.5):
            return False
        return True
    except:
        return False

print()
print("--------------------------------------------------------------------------------")
print("SMU S/U Decision Maker")
print("--------------------------------------------------------------------------------")
print()

cgpa = float(input("what is your current GPA (cGPA)? (Including this sem): "))
num_of_gmod = float(input("How many graded credit units (CU) have you taken? (Including this sem): "))

# number of mods this sem
num_of_mod = input("How many graded mods are you taking this sem?: ")

while not (num_of_mod.isdigit() and int(num_of_mod) > 0):
    print("Invalid number of modules")
    num_of_mod = input("How many graded mods are you taking this sem?: ")

p = inflect.engine()
this_sem = []

print("--------------------------------------------------------------------------------")

for i in range (1, int(num_of_mod) + 1):
    print("\nFor the " + p.ordinal(i) + " mod,")
    print("How many credit unit (CU) is the module?:")
    cu = input()

    while not check_cu(cu):
        print("Invalid CU")
        print("How many credit unit (CU) is the module?:")
        cu = input()

    print("What is the grade achieved?")
    grade = str(input())

    while not(check_grade_input(grade.upper())):
        print("Invalid Grade")
        print("What is the grade achieved?")
        grade = str(input())

    this_sem.append([grade.upper(), float(cu), grades_dict[grade.upper()]])
    this_sem = sorted(sorted(this_sem, key= lambda x: x[1]), key = lambda x: x[-1], reverse=True)

print("--------------------------------------------------------------------------------")

cgpa *= num_of_gmod

max_gpa = {'gpa': 0, 'mods': []}

counter = 0
for i in this_sem[::-1]:
    num_of_gmod -= i[1]
    cgpa -= i[2]
    current_gpa = round(cgpa/num_of_gmod,2)
    
    if (current_gpa > max_gpa['gpa']):
        max_gpa['gpa'] = current_gpa
        max_gpa['mods'].append(i)

    if(counter == 0):
        print("If you S/U 1 " + i[0] + " module with " + str(i[1]) + " credit unit, you will get a cumulative GPA of: " + str(current_gpa))
    else:
        print("If you S/U another 1 " + i[0] + " module with " + str(i[1]) + " credit unit, you will get a cumulative GPA of: " + str(current_gpa))
    
    counter += 1

print("--------------------------------------------------------------------------------")

print("To get the highest GPA of " + str(max_gpa['gpa']) + " with least number of S/U:")
print("You should S/U the following modules")
for i in max_gpa['mods']:
    print("\tThe " + str(i[1]) + " cu module with grade of " + str(i[0]))

print("--------------------------------------------------------------------------------")

# print("The highest GPA you can get is 3.36 with 3 S/U (2 B modules, 1 B- module)")

#Include this sem CGPA = 3.28
#Number of mods (include this sem) = 18
#this sem take 5 mods
#if SU B- only 3.25
#if SU B- and B (3 mods) = 3.28


# {3.36: {mods:{"B":2, "B-":1}}}