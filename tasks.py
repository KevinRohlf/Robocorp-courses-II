from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
        
    )
    download_csv_file()
    open_robot_order_website()
    orders()
    archive_receipts()


def open_robot_order_website():
    """open the website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    


def download_csv_file():
    """Downloads CSV file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)


def fill_the_form(order):
    """fill the form and order a robot"""
    page = browser.page()
    page.click("button:text('I guess so...')")
    page.select_option("#head", str(order["Head"]))
    page.check(f"#id-body-{str(order['Body'])}")
    page.fill('.form-control', str(order["Legs"]))
    page.fill("#address", str(order["Address"]))
    page.click("button:text('Order')")
    submit_form(order["Order number"])


def orders():
    """starts fill_the_form & embed_screenshot_to_receipt for every row in the csv file"""
    orders = get_orders()
    for row in orders:
        fill_the_form(row)
        embed_screenshot_to_receipt(f"output/screen-{row['Order number']}.png", f"output/receipt/order-{row['Order number']}.pdf")

def get_orders():
    """get the orders from CSV file"""
    csv = Tables()
    orders = csv.read_table_from_csv(path="orders.csv", header=True)
    return orders

def save_order_html(order_number):
    """save the order HTML in PDF file & starts the screenshot_robot function"""
    page = browser.page()   
    order_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(order_html, f"output/receipt/order-{order_number}.pdf")
    screenshot_robot(order_number)
    page.click("button:text('Order another robot')")
    
def screenshot_robot(order_number):
    """take a screenshot from the robot preview"""
    page = browser.page()
    loc = page.locator("#robot-preview-image")
    loc.screenshot(path=f"output/screen-{order_number}.png")
    
def embed_screenshot_to_receipt(screenshot, pdf_file):
    """merge the Screenshot to the receipt PDF file"""
    pdf = PDF()
    list = [
        f"{screenshot}:align=center",
    ]
    pdf.add_files_to_pdf(files=list, target_document=pdf_file, append=True)

def submit_form(order_number):
    """Submit the form with error check"""
    page = browser.page()
    visible = page.locator("#receipt").is_visible()    
    if visible :
        save_order_html(order_number)
    else:
        page.click("button:text('Order')")
        submit_form(order_number)
        
def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip(folder="output/receipt", archive_name="output/receipts.zip")
        


    
