import os
import smtplib
from urllib import request
from bs4 import BeautifulSoup
import time
import datetime
from dotenv import load_dotenv
from tkinter import *
from tkinter import messagebox
import threading
import re

load_dotenv()



def button_click():
    validate_inputs()
    try:
        # Start a new thread to run the price check
        threading.Thread(target=check_price_daily).start()
    except Exception as e:
        print(e)

# Create the main window
window = Tk()
window.title("Amazon Price Tracker")

# Set the size of the window
window.geometry('600x300')

# Create the input labels
link_label = Label(window, text="Enter the Amazon Product Link:")
link_label.grid(column=0, row=0, padx=10, pady=10)
threshold_label = Label(window, text="Enter the Price Threshold in Pounds:")
threshold_label.grid(column=0, row=1, padx=10, pady=10)
email_label = Label(window, text="Enter the Receiver Email Address:")
email_label.grid(column=0, row=2, padx=10, pady=10)

# Create the input fields
link_field = Entry(window, width=50)
link_field.grid(column=1, row=0, padx=10, pady=10)
threshold_field = Entry(window, width=10)
threshold_field.grid(column=1, row=1,sticky="w", padx=10, pady=10)
email_field = Entry(window, width=50)
email_field.grid(column=1, row=2, padx=10, pady=10)

# Create the output label
btn = Button(window, text="Check", command=button_click)
btn.grid(column=1, row=3, sticky="w", padx=20)

# Create the next check label
next_check_label = Label(window, text="")
next_check_label.grid(column=0, row=4, padx=10, pady=10)

# User-Agent header to avoid being detected as a bot
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

def validate_inputs():
    link = link_field.get()
    threshold = threshold_field.get()
    email = email_field.get()

    # Check if the link is valid
    if not link.startswith("https://www.amazon"):
        messagebox.showerror("Error", "Invalid Amazon product link")
        return False

    # Check if the threshold is a valid number
    try:
        float(threshold)
    except ValueError:
        messagebox.showerror("Error", "Invalid price threshold")
        return False

    # Check if the email is in the correct format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        messagebox.showerror("Error", "Invalid email address")
        return False

    return True

def check_price():
    # Remove any existing text from the next check label
    next_check_label.config(text="")
    # Retrieve the HTML for the Amazon product page
    URL = link_field.get()
    req = request.Request(URL, headers=headers)
    html = request.urlopen(req).read()

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Extract the product title and price
    title = soup.find(id='productTitle').get_text().strip()
    price = soup.find(class_='a-offscreen').get_text()

    # Convert the price to a float
    converted_price = float(price.replace('£', '').replace(',', ''))

    # Print the product title and price
    print(f"Title: {title}")
    print(f"Price: £{converted_price}")

    # Check if the price has decreased
    threshold = float(threshold_field.get())
    if converted_price < threshold:
        send_email()

def check_price_daily():
    while True:
        # Get the current time
        now = datetime.datetime.now()

        # Check if the current time is after 8:00 AM (or any other time you want to schedule the check)
        if now.hour >= 8:
            # Check the price
            try:
                check_price()
            except Exception as e:
                print(e)

            # Calculate the next check time (24 hours from now)
            next_check = now + datetime.timedelta(days=1)
            next_check_str = next_check.strftime("%Y-%m-%d %H:%M:%S")

            # Update the next check label
            next_check_label.config(text=f"Next check: {next_check_str}")

            # Wait for 24 hours before checking the price again
            time.sleep(24 * 60 * 60)
        else:
            # Wait for an hour before checking again
            time.sleep(60 * 60)

def send_email():
    # Your email credentials
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    receiver_email = email_field.get()

    # Email message
    message = f"From: {sender_email}\nTo: {receiver_email}\nSubject: Amazon Price Alert!\n\nThe price of the product has fallen below £{threshold_field.get()}. Check it out at: {link_field.get()}"

    message = message.encode('utf-8')  # Encode the message using UTF-8

    # Send the email using SMTP
    with smtplib.SMTP('smtp.office365.com', 587) as smtp:
        smtp.starttls()
        smtp.login(sender_email, sender_password)
        smtp.sendmail(sender_email, receiver_email, message)

# Function to handle the button click event


def main():
       window.mainloop()

if __name__ == '__main__':
    main()