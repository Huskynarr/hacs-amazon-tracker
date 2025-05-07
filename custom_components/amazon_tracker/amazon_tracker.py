"""Amazon Package Tracker integration."""
import logging
import re
from typing import Any
import aiohttp
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)

async def fetch_amazon_packages(email: str, password: str) -> list[dict[str, Any]]:
    """Fetch packages from Amazon."""
    async with aiohttp.ClientSession() as session:
        try:
            # First, get the login page to get the necessary cookies
            async with session.get("https://www.amazon.de/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.de%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=deflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0") as response:
                if response.status != 200:
                    _LOGGER.error("Failed to get login page. Status: %s, URL: %s", response.status, response.url)
                    raise Exception(f"Failed to get login page: {response.status}")
                
                # Get the login form
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find the login form
                form = soup.find("form", {"name": "signIn"})
                if not form:
                    _LOGGER.error("Login form not found in HTML: %s", html[:500])  # Log first 500 chars of HTML
                    raise Exception("Login form not found")
                
                # Get the form action URL
                action_url = form.get("action")
                if not action_url:
                    _LOGGER.error("Form action URL not found in form: %s", form)
                    raise Exception("Form action URL not found")
                
                # Prepare login data
                login_data = {
                    "email": email,
                    "password": password,
                }
                
                # Add any hidden fields from the form
                for hidden in form.find_all("input", type="hidden"):
                    login_data[hidden.get("name")] = hidden.get("value")
                
                # Submit the login form
                async with session.post(action_url, data=login_data) as login_response:
                    if login_response.status != 200:
                        _LOGGER.error("Login failed. Status: %s, URL: %s", login_response.status, login_response.url)
                        raise Exception(f"Login failed: {login_response.status}")
                    
                    # Now get the order history
                    async with session.get("https://www.amazon.de/gp/css/order-history") as response:
                        if response.status != 200:
                            _LOGGER.error("Failed to get order history. Status: %s, URL: %s", response.status, response.url)
                            raise Exception(f"Failed to get order history: {response.status}")
                        
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find all order cards
                        order_cards = soup.find_all("li", class_="order-card__list")
                        packages = []

                        for card in order_cards:
                            try:
                                # Extract order number
                                order_number = card.find("span", class_="a-color-secondary", dir="ltr").text.strip()
                                
                                # Extract order date
                                order_date = card.find("span", class_="a-size-base a-color-secondary aok-break-word").text.strip()
                                
                                # Extract delivery status
                                delivery_status = card.find("span", class_="delivery-box__secondary-text").text.strip()
                                
                                # Extract estimated delivery
                                delivery_estimate = card.find("span", class_="delivery-box__primary-text").text.strip()
                                delivery_estimate = re.search(r"(\d{1,2}\.\s\w+\s-\s\d{1,2}\.\s\w+)", delivery_estimate).group(1)
                                
                                # Extract tracking link
                                tracking_link = card.find("a", href=lambda x: x and "ship-track" in x)
                                if tracking_link:
                                    tracking_url = "https://www.amazon.de" + tracking_link['href']
                                    
                                    # Get tracking details
                                    async with session.get(tracking_url) as tracking_response:
                                        if tracking_response.status == 200:
                                            tracking_html = await tracking_response.text()
                                            tracking_soup = BeautifulSoup(tracking_html, 'html.parser')
                                            
                                            # Extract carrier and tracking number
                                            carrier_info = tracking_soup.find("div", class_="pt-delivery-card-trackingId")
                                            if carrier_info:
                                                carrier_text = carrier_info.text.strip()
                                                carrier = carrier_text.split(" mit ")[1].split("Trackingnummer")[0].strip()
                                                tracking_number = carrier_text.split("Trackingnummer")[1].strip()
                                                
                                                # Extract products
                                                products = []
                                                product_links = card.find_all("a", class_="a-link-normal", href=lambda x: x and "/dp/" in x)
                                                for product in product_links:
                                                    products.append(product.text.strip())
                                                
                                                packages.append({
                                                    "tracking_number": tracking_number,
                                                    "carrier": carrier,
                                                    "estimated_delivery": delivery_estimate,
                                                    "order_date": order_date,
                                                    "order_number": order_number,
                                                    "product_name": ", ".join(products),
                                                    "status": delivery_status,
                                                })
                            except Exception as err:
                                _LOGGER.error("Error parsing order card: %s", err)
                                continue

                        return packages

        except Exception as err:
            _LOGGER.error("Error fetching Amazon data: %s", err)
            return [] 