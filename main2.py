import os
import smtplib
from urllib import request
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv
from tkinter import *
from tkinter import messagebox

load_dotenv()
# Create the product list
product_list = []

def add_product():
    # Retrieve the product details
    link = link_field.get()
    threshold = threshold_field.get()
    email = email_field.get()

    # Validate the product details
    if not link:
        messagebox.showerror("Error", "Please enter a product link.")
        return
    if not threshold:
        messagebox.showerror("Error", "Please enter a price threshold.")
        return
    if not email:
        messagebox.showerror("Error", "Please enter an email address.")
        return

    # Add the product to the list
    product_list.append((link, threshold, email))

    # Clear the input fields
    link_field.delete(0, END)
    threshold_field.delete(0, END)
    email_field.delete(0, END)

    # Update the product list
    update_product_list()

def clear_products():
    # Clear the product list
    global product_list
    product_list = []

    # Update the product list
    update_product_list()

def update_product_list():
    # Clear the output text area
    output_text.delete('1.0', END)

# Create the main window
window = Tk()
window.title("Amazon Price Tracker")

# Set the size of the window
window.geometry('600x600')

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
threshold_field = Entry(window, width=50)
threshold_field.grid(column=1, row=1, padx=10, pady=10)
email_field = Entry(window, width=50)
email_field.grid(column=1, row=2, padx=10, pady=10)

# Create the output label
output_label = Label(window, text="Output:")
output_label.grid(column=0, row=4, padx=10, pady=10, sticky="w")

# Create the output text area
output_text = Text(window, height=10, width=50)
output_text.grid(column=0, row=5, padx=10, pady=10, columnspan=2)

# Create the add button
add_button = Button(window, text="Add", command=add_product)
add_button.grid(column=0, row=3, sticky="w", padx=10, pady=10)

# Create the clear button
clear_button = Button(window, text="Clear", command=clear_products)
clear_button.grid(column=1, row=3, sticky="e", padx=10, pady=10)



# User-Agent header to avoid being detected as a bot
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

def check_price():
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