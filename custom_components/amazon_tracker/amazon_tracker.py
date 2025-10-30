"""Amazon Package Tracker integration."""
import logging
import re
from typing import Any
import aiohttp
from bs4 import BeautifulSoup

from .const import AMAZON_DOMAINS

_LOGGER = logging.getLogger(__name__)

async def fetch_amazon_packages(email: str, password: str, domain: str = "amazon.de") -> list[dict[str, Any]]:
    """Fetch packages from Amazon."""
    if domain not in AMAZON_DOMAINS:
        _LOGGER.error("Unsupported Amazon domain: %s", domain)
        return []
    
    base_url = AMAZON_DOMAINS[domain]["base_url"]
    
    async with aiohttp.ClientSession() as session:
        try:
            # First, get the login page to get the necessary cookies
            login_url = f"{base_url}/ap/signin?openid.pape.max_auth_age=0&openid.return_to={base_url}%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=deflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
            async with session.get(login_url) as response:
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
                    order_history_url = f"{base_url}/gp/css/order-history"
                    async with session.get(order_history_url) as response:
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
                                    tracking_url = base_url + tracking_link['href']
                                    
                                    # Get tracking details
                                    async with session.get(tracking_url) as tracking_response:
                                        if tracking_response.status == 200:
                                            tracking_html = await tracking_response.text()
                                            tracking_soup = BeautifulSoup(tracking_html, 'html.parser')
                                            
                                            # Extract carrier and tracking number
                                            carrier_info = tracking_soup.find("div", class_="pt-delivery-card-trackingId")
                                            if carrier_info:
                                                carrier_text = carrier_info.text.strip()
                                                
                                                # Language-specific parsing patterns
                                                # Try to extract tracking number using common patterns
                                                carrier = None
                                                tracking_number = None
                                                
                                                # Pattern for German: "mit [carrier] Trackingnummer [number]"
                                                if " mit " in carrier_text and "Trackingnummer" in carrier_text:
                                                    try:
                                                        carrier = carrier_text.split(" mit ")[1].split("Trackingnummer")[0].strip()
                                                        tracking_number = carrier_text.split("Trackingnummer")[1].strip()
                                                    except IndexError:
                                                        pass
                                                
                                                # Pattern for English: "with [carrier] Tracking ID [number]" or "by [carrier] Tracking ID [number]"
                                                elif ("with " in carrier_text or "by " in carrier_text) and "Tracking ID" in carrier_text:
                                                    try:
                                                        if "with " in carrier_text:
                                                            carrier = carrier_text.split("with ")[1].split("Tracking ID")[0].strip()
                                                        else:
                                                            carrier = carrier_text.split("by ")[1].split("Tracking ID")[0].strip()
                                                        tracking_number = carrier_text.split("Tracking ID")[1].strip()
                                                    except IndexError:
                                                        pass
                                                
                                                # Pattern for French: "avec [carrier] Numéro de suivi [number]"
                                                elif "avec " in carrier_text and "Numéro de suivi" in carrier_text:
                                                    try:
                                                        carrier = carrier_text.split("avec ")[1].split("Numéro de suivi")[0].strip()
                                                        tracking_number = carrier_text.split("Numéro de suivi")[1].strip()
                                                    except IndexError:
                                                        pass
                                                
                                                # Fallback: try to extract tracking number with regex
                                                if not tracking_number:
                                                    import re
                                                    # Look for common tracking number patterns
                                                    tracking_match = re.search(r'[A-Z0-9]{10,}', carrier_text)
                                                    if tracking_match:
                                                        tracking_number = tracking_match.group(0)
                                                        # Carrier is everything before the tracking number
                                                        carrier = carrier_text.split(tracking_number)[0].strip()
                                                
                                                # Only add package if we successfully extracted tracking info
                                                if tracking_number and carrier:
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