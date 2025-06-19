from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.core.mail import send_mail
from datetime import datetime as dt

from gtts import gTTS
from .models import *
import datetime
import os

# Create your views here.


def index(request):
    return render(request, "index.html")


def contact(request):
    return render(request, "contact.html")


def signin(request):
    if request.POST:
        email = request.POST["email"]
        passw = request.POST["password"]
        data = authenticate(username=email, password=passw)
        if data is not None:
            login(request, data)
            print("Data")
            if data.is_active:
                if data.userType == "User":
                    print("User")
                    id = data.id
                    request.session["uid"] = id
                    resp = '<script>alert("Login Success"); window.location.href = "/userHome";</script>'
                    return HttpResponse(resp)
                elif data.userType == "Admin":
                    print("Admin")
                    resp = '<script>alert("Login Success"); window.location.href = "/adminHome";</script>'
                    return HttpResponse(resp)
            else:
                print("Sorry You Are Not Approved")
                resp = '<script>alert("Sorry You Are Not Approved"); window.location.href = "/adminHome";</script>'
                return HttpResponse(resp)
        else:
            resp = '<script>alert("Sorry You Are Not Approved..😥");window.location.href="/login"</script>'
            return HttpResponse(resp)
    return render(request, "COMMON/login.html")


def register(request):
    current_datetime = datetime.date.today()
    current_date = current_datetime.strftime("%Y-%m-%d")
    print(current_date)
    if request.POST:
        name = request.POST["name"]
        email = request.POST["email"]
        gender = request.POST["gender"]
        dob = request.POST["dob"]
        phone = request.POST["phone"]
        password = request.POST["password"]
        address = request.POST["address"]
        image = request.FILES["imgfile"]

        if Login.objects.filter(username=email).exists():
            return HttpResponse(
                "<script>alert('Email already Exists Added');window.location.href='/registration'</script>"
            )
        else:
            logQry = Login.objects.create_user(
                username=email,
                password=password,
                userType="User",
                viewPass=password,
                is_active=0,
            )
            logQry.save()
            regQry = Person.objects.create(
                name=name,
                email=email,
                gender=gender,
                dob=dob,
                phone=phone,
                address=address,
                image=image,
                loginid=logQry,
            )
            regQry.save()
            return HttpResponse(
                "<script>alert('Registration Successfull');window.location.href='/login'</script>"
            )
    return render(request, "COMMON/register.html", {"current_date": current_date})


def udp(request):
    abc = Login.objects.get(username="admin@gmail.com")
    abc.set_password("admin")
    abc.save()
    return HttpResponse("Success")


################################################***ADMIN***################################################


def adminHome(request):
    return render(request, "ADMIN/adminHome.html")


def viewUsers(request):
    data = Person.objects.all()
    return render(request, "ADMIN/viewUsers.html", {"data": data})


def approveUser(request):
    id = request.GET["id"]
    approve = Login.objects.filter(id=id).update(is_active=1)
    return HttpResponse(
        "<script>alert('Approved');window.location.href='/viewusers'</script>"
    )


def rejectUser(request):
    id = request.GET["id"]
    approve = Login.objects.filter(id=id).update(is_active=0)
    return HttpResponse(
        "<script>alert('Rejected');window.location.href='/viewusers'</script>"
    )


def deleteUser(request):
    id = request.GET["id"]
    delete = Login.objects.filter(id=id).delete()
    return HttpResponse(
        "<script>alert('Deleted');window.location.href='/viewusers'</script>"
    )


def approveRequest(request):
    id = request.GET["id"]
    upDate = Person.objects.filter(loginid=id).update(status="Approved")
    return HttpResponse(
        "<script>alert('Approved');window.location.href='/viewusers'</script>"
    )


def viewFeedback(request):
    data = Feedback.objects.all()
    return render(request, "ADMIN/viewFeedback.html", {"data": data})


################################################***USER***################################################


def userHome(request):
    return render(request, "USER/userHome.html")


def profile(request):
    uid = request.session["uid"]
    data = Person.objects.get(loginid=uid)
    return render(request, "USER/profile.html", {"data": data})


def requestUpdation(request):
    id = request.GET["id"]
    requestUpdate = Person.objects.filter(loginid=id).update(status="Requested")
    return HttpResponse(
        "<script>alert('Requested');window.location.href='/profile'</script>"
    )


def updateProfile(request):
    current_datetime = datetime.date.today()
    current_date = current_datetime.strftime("%Y-%m-%d")
    print(current_date)
    uid = request.session["uid"]
    data = Person.objects.get(loginid=uid)
    if request.POST:
        name = request.POST["name"]
        email = request.POST["email"]
        gender = request.POST["gender"]
        dob = request.POST["dob"]
        phone = request.POST["phone"]
        password = request.POST["password"]
        address = request.POST["address"]
        image = request.FILES.get("imgfile")

        if image:
            data = Person.objects.get(loginid=uid)
            data.image = image
            data.save()
        if password:
            data = Login.objects.get(id=uid)
            data.set_password(password)
            data.save()
        update = Person.objects.filter(loginid=uid).update(
            name=name,
            email=email,
            phone=phone,
            address=address,
            gender=gender,
            dob=dob,
            status="View",
        )
        logUpdate = Login.objects.filter(id=uid).update(username=email)
        return redirect("/profile")
    return render(
        request, "USER/updateProfile.html", {"data": data, "current_date": current_date}
    )


def addFeedback(request):
    uid = request.session["uid"]
    UID = Person.objects.get(loginid=uid)
    data = Feedback.objects.filter(uid__loginid=uid)
    if request.POST:
        title = request.POST["title"]
        feedback = request.POST["feedback"]
        add = Feedback.objects.create(uid=UID, title=title, feedback=feedback)
        add.save()
        return HttpResponse(
            "<script>alert('Feedback Added');window.location.href='/addFeedback'</script>"
        )
    return render(request, "USER/addFeedback.html", {"data": data})


from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
from PIL import Image
from .models import Person, Message
import os

def hide_text_in_image(image, text, output_path):
    """
    Hides a given text message inside an image using LSB steganography.
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Convert text to binary with a stop sequence
    binary_text = ''.join(format(ord(char), '08b') for char in text) + '1111111111111110'

    data_index = 0
    pixels = list(image.getdata())
    new_pixels = []

    for pixel in pixels:
        new_pixel = list(pixel)
        for i in range(3):  # Modify RGB channels
            if data_index < len(binary_text):
                # Replace the least significant bit with the binary text bit
                new_pixel[i] = new_pixel[i] & ~1 | int(binary_text[data_index])
                data_index += 1
        new_pixels.append(tuple(new_pixel))

    # Create a new image with the modified pixels
    stego_image = Image.new(image.mode, image.size)
    stego_image.putdata(new_pixels)
    stego_image.save(output_path)
    return output_path

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import os
from io import BytesIO


def hide_text_in_image(image, text):
    """
    Hides a given text message inside an image using LSB steganography.
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Convert text to binary with a stop sequence
    binary_text = ''.join(format(ord(char), '08b') for char in text) + '1111111111111110'

    data_index = 0
    pixels = list(image.getdata())
    new_pixels = []

    for pixel in pixels:
        new_pixel = list(pixel)
        for i in range(3):  # Modify RGB channels
            if data_index < len(binary_text):
                # Replace the least significant bit with the binary text bit
                new_pixel[i] = new_pixel[i] & ~1 | int(binary_text[data_index])
                data_index += 1
        new_pixels.append(tuple(new_pixel))

    # Create a new image with the modified pixels
    stego_image = Image.new(image.mode, image.size)
    stego_image.putdata(new_pixels)
    return stego_image

def compose(request):
    print("[DEBUG] Compose function called.")
    uid = request.session.get("uid")
    print(f"[DEBUG] Logged in user ID: {uid}")
    sender = Person.objects.get(loginid=uid)
    print(f"[DEBUG] Sender email: {sender.email}")
    msg = ""

    if "sent" in request.POST:
        print("[DEBUG] Handling 'sent' action...")
        receiver = request.POST["email"]
        subject = request.POST["subject"]
        password = request.POST["password"]
        message = request.POST["message"]
        image = request.FILES["imgfile"]
        attachment = request.FILES.get("attachment")
        print(f"[DEBUG] Receiver email: {receiver}")
        print(f"[DEBUG] Subject: {subject}")
        print(f"[DEBUG] Password: {password}")
        print(f"[DEBUG] Message: {message}")

        email_subject = "Password for Opening the File"
        email_body = f"The password for opening the specific file is: {password}"

        if Person.objects.filter(email=receiver).exists():
            print("[DEBUG] Receiver exists in the database.")
            receiver_id = Person.objects.get(email=receiver)
            recipient_list = [receiver]

            # Open the uploaded image and embed the message
            img = Image.open(image)
            print("[DEBUG] Opened uploaded image.")
            print(f"[DEBUG] Image details - Size: {img.size}, Mode: {img.mode}, Format: {img.format}")
            print(f"[DEBUG] Image bytes: {image.read()[:100]}... [truncated for display]")  # Print the first 100 bytes

            # Reset the file pointer to avoid read issues later
            image.seek(0)

            stego_image = hide_text_in_image(img, message)

            # Save the stego image to a buffer
            buffer = BytesIO()
            stego_image.save(buffer, format="PNG")
            buffer.seek(0)
            print("[DEBUG] Stego image saved to buffer.")

            # Convert buffer to a Django-compatible file
            stego_file = SimpleUploadedFile(
                name=f"stego_image_{uid}.png",
                content=buffer.read(),
                content_type="image/png"
            )
            print("[DEBUG] Stego image converted to Django-compatible file.")

            # Send email
            print("[DEBUG] Sending email...")
            result = send_mail(
                subject=email_subject,
                message=email_body,
                from_email=sender.email,
                recipient_list=recipient_list,
            )

            if result:
                print("[DEBUG] Email sent successfully.")
                # Save the message with the stego image
                sent_msg = Message.objects.create(
                    sender=sender,
                    receiver=receiver_id,
                    subject=subject,
                    msg=message,
                    password=password,
                    file=stego_file,
                    attachment=attachment if attachment else None,
                    status="Sent",
                )
                sent_msg.save()
                print("[DEBUG] Message saved to the database.")
                return HttpResponse(
                    "<script>alert('Message Sent Successfully');window.location.href='/compose'</script>"
                )
            else:
                print("[DEBUG] Email sending failed.")
                return HttpResponse(
                    "<script>alert('Something went wrong');window.location.href='/compose'</script>"
                )
        else:
            print("[DEBUG] Receiver does not exist in the database.")
            msg = "User does not exist"
            return render(request, "USER/compose.html", {"msg": msg})

    elif "save" in request.POST:
        print("[DEBUG] Handling 'save' action...")
        receiver = request.POST["email"]
        subject = request.POST["subject"]
        password = request.POST["password"]
        message = request.POST["message"]
        image = request.FILES["imgfile"]
        print(f"[DEBUG] Saving message for receiver: {receiver}")
        print(f"[DEBUG] Uploaded image - Name: {image.name}, Size: {image.size}")

        receiver_id = Person.objects.get(email=receiver)
        sent_msg = Message.objects.create(
            sender=sender,
            receiver=receiver_id,
            subject=subject,
            msg=message,
            password=password,
            file=image,
            status="Save",
        )
        sent_msg.save()
        print("[DEBUG] Message saved successfully.")

    print("[DEBUG] Render compose page.")
    return render(request, "USER/compose.html")


def inbox(request):
    uid = request.session["uid"]
    inboxData = Message.objects.filter(receiver__loginid=uid).order_by("-date")
    print(inboxData)
    return render(request, "USER/inbox.html", {"inboxData": inboxData})


def readMail(request):
    uid = request.session["uid"]
    id = request.GET["id"]
    data = Message.objects.get(id=id)

    if request.POST:
        password = request.POST["password"]
        if Message.objects.filter(Q(id=id) & Q(password=password)).exists():
            mailData = Message.objects.get(Q(id=id) & Q(password=password))
            if mailData:
                return render(
                    request,
                    "USER/readMail.html",
                    {"data": data.file, "mailData": mailData},
                )
        else:
            print("Else")
            return HttpResponse(
                f"<script>alert('Incorrect Password');window.location.href='/readMail?id={id}'</script>"
            )
    return render(request, "USER/readMail.html", {"data": data.file})


def text_to_audio(text, output_file="output.mp3", language="en"):
    try:
        tts = gTTS(text=text, lang=language)
        tts.save(output_file)
        print(f"Text converted to audio and saved as '{output_file}'")
        os.system(f"start {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


def download(request):
    current_datetime = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
    text = request.GET["text"]
    id = request.GET["id"]
    print(text)
    output_file_path = f"./static/downloads/output_{current_datetime}_{id}.mp3"
    text_to_audio(text, output_file_path)
    return redirect(f"/readMail?id={id}")


def send_email(request):
    if request.POST:
        sub = request.POST["subject"]
        msg = request.POST["message"]
        receiver = request.POST["receiver"]
        from_email = "forpythonjava@gmail.com"
        recipient_list = [receiver]
        result = send_mail(sub, msg, from_email, recipient_list)
        print(result)
    return render(request, "sendMail.html")
