from lxml import etree
import os
from datetime import datetime
import json
import xmltodict
import requests

def fetch_and_parse_xml_feed(url: str, hash: str) -> dict:
    """
    Fetches XML data from a given URL and converts it to a dictionary.
    
    Args:
        url (str): The URL of the XML feed.
        
    Returns:
        dict: The XML data converted to a dictionary.
    """
    try:
        response = requests.get(url, params={'hash': hash})
        response.raise_for_status()  # Raise an error for bad responses
        xml_data = response.content
        parsed_data = xmltodict.parse(xml_data)
        return parsed_data['PRODUCTS']['PRODUCT']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching XML feed: {e}")
        return None

def parse_xml_to_etree(data):
    """Parse XML data to an ElementTree object"""
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(data, parser)
        return tree
    except etree.XMLSyntaxError as e:
        print(f"Error parsing XML data: {e}")
        return None

def save_xml(tree, file_path):
    """Save XML tree to file"""
    try:
        tree.write(file_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
        print(f"Successfully saved to {file_path}")
    except Exception as e:
        print(f"Error saving XML file: {e}")

def add_element(parent, tag, text=None, attributes=None):
    """Add new element to parent"""
    if ':' in tag:
        prefix, tag_name = tag.split(':')
        namespace = parent.nsmap.get(prefix)
        if namespace:
            element = etree.SubElement(parent, f"{{{namespace}}}{tag_name}")
        else:
            raise ValueError(f"Namespace prefix '{prefix}' not found in parent's nsmap")
    else:
        element = etree.SubElement(parent, tag)
    
    if text:
        element.text = text
    if attributes:
        for key, value in attributes.items():
            element.set(key, value)
    return element

def modify_element(element, new_text=None, new_attributes=None):
    """Modify existing element"""
    if new_text is not None:
        element.text = new_text
    if new_attributes:
        for key, value in new_attributes.items():
            element.set(key, value)

def delete_element(parent, element):
    """Delete element from parent"""
    parent.remove(element)

def create_invoice_item_home_currency(root, item_data):
    """Create a new invoice item in the XML tree
    Invoice item structure:
        <inv:invoiceItem>
            <inv:text>Set Stripes Callin</inv:text>
            <inv:quantity>1</inv:quantity>
            <inv:unit>ks</inv:unit>
            <inv:payVAT>false</inv:payVAT>
            <inv:rateVAT>high</inv:rateVAT>
            <inv:homeCurrency>
                <typ:unitPrice>1900</typ:unitPrice>
                <typ:price>1570</typ:price>
                <typ:priceVAT>330</typ:priceVAT>
            </inv:homeCurrency>
            <inv:stockItem>
                <typ:stockItem>
                    <typ:ids>102246_100239</typ:ids>
                </typ:stockItem>
            </inv:stockItem>
            <inv:code>102246_100239</inv:code>
        </inv:invoiceItem>
    """
    namespaces = {
        'dat': root.nsmap['dat'],
        'inv': root.nsmap['inv'],
        'typ': root.nsmap['typ']
    }
    
    invoice_item = add_element(root, 'inv:invoiceItem')
    add_element(invoice_item, 'inv:text', item_data['text'])
    add_element(invoice_item, 'inv:quantity', str(item_data['quantity']))
    add_element(invoice_item, 'inv:unit', item_data['unit'])
    add_element(invoice_item, 'inv:payVAT', str(item_data['payVAT']).lower())
    add_element(invoice_item, 'inv:rateVAT', item_data['rateVAT'])
    
    home_currency = add_element(invoice_item, 'inv:homeCurrency')
    add_element(home_currency, 'typ:unitPrice', str(item_data['unitPrice']))
    add_element(home_currency, 'typ:price', str(item_data['price']))
    add_element(home_currency, 'typ:priceVAT', str(item_data['priceVAT']))
    
    stock_item = add_element(invoice_item, 'inv:stockItem')
    stock_item_elem = add_element(stock_item, 'typ:stockItem')
    add_element(stock_item_elem, 'typ:ids', item_data['stockItemId'])
    
    # Add code only if it's not shipping or billing
    if not any(prefix in item_data['code'] for prefix in ['SHIPPING', 'BILLING']):
        add_element(invoice_item, 'inv:code', item_data['code'])
    
    return invoice_item

def create_invoice_item_foreign_currency(root, item_data):
    """Create a new invoice item in the XML tree
    Invoice item structure:
        <inv:invoiceItem>
            <inv:text>Set Stripes Callin</inv:text>
            <inv:quantity>1</inv:quantity>
            <inv:unit>ks</inv:unit>
            <inv:payVAT>false</inv:payVAT>
            <inv:rateVAT>high</inv:rateVAT>
            <inv:foreignCurrency>
                <typ:unitPrice>1900</typ:unitPrice>
                <typ:price>1570</typ:price>
                <typ:priceVAT>330</typ:priceVAT>
            </inv:foreignCurrency>
            <inv:stockItem>
                <typ:stockItem>
                    <typ:ids>102246_100239</typ:ids>
                </typ:stockItem>
            </inv:stockItem>
            <inv:code>102246_100239</inv:code>
        </inv:invoiceItem>
    """
    namespaces = {
        'dat': root.nsmap['dat'],
        'inv': root.nsmap['inv'],
        'typ': root.nsmap['typ']
    }

    invoice_item = add_element(root, 'inv:invoiceItem')
    add_element(invoice_item, 'inv:text', item_data['text'])
    add_element(invoice_item, 'inv:quantity', str(item_data['quantity']))
    add_element(invoice_item, 'inv:unit', item_data['unit'])
    add_element(invoice_item, 'inv:payVAT', str(item_data['payVAT']).lower())
    add_element(invoice_item, 'inv:rateVAT', item_data['rateVAT'])
    
    home_currency = add_element(invoice_item, 'inv:foreignCurrency')
    add_element(home_currency, 'typ:unitPrice', str(item_data['unitPrice']))
    add_element(home_currency, 'typ:price', str(item_data['price']))
    add_element(home_currency, 'typ:priceVAT', str(item_data['priceVAT']))
    
    stock_item = add_element(invoice_item, 'inv:stockItem')
    stock_item_elem = add_element(stock_item, 'typ:stockItem')
    add_element(stock_item_elem, 'typ:ids', item_data['stockItemId'])
    
    # Add code only if it's not shipping or billing
    if not any(prefix in item_data['code'] for prefix in ['SHIPPING', 'BILLING']):
        add_element(invoice_item, 'inv:code', item_data['code'])
    
    return invoice_item 

def update_unit_prices(root, bank_id, account_no, bank_code, const_symbol, store_id, feed_url, hash, eur_rate):
    """
    Update unitPrice to be the sum of price and priceVAT in homeCurrency for all invoice items
    
    Args:
        root: XML root element
        bank_id (str): Bank ID
        account_no (str): Account number
        bank_code (str): Bank code
        const_symbol (str): Symbol constant
        store_id (str): Store ID
        feed_url (str): URL of the XML feed
        hash (str): Hash for authentication
        eur_rate (float): EUR exchange rate
    """
    namespaces = {
        'dat': root.nsmap['dat'],
        'inv': root.nsmap['inv'],
        'typ': root.nsmap['typ']
    }

    vat_rate = {
        '21': 'high',
        '12': 'medium',
        '10': 'low',
    }

    # Remove inv:code only for shipping and billing items
    for invoice_item in root.findall('.//inv:invoiceItem', namespaces):
        code_elem = invoice_item.find('inv:code', namespaces)
        if code_elem is not None:
            code_value = code_elem.text
            if code_value and ('SHIPPING' in code_value or 'BILLING' in code_value):
                delete_element(invoice_item, code_elem)

    # load XML feed
    xml_feed = fetch_and_parse_xml_feed(feed_url, hash)

    for inv_item in root.findall('.//inv:invoiceItem', namespaces):
        stock_item = inv_item.find('inv:stockItem', namespaces)
        # check if stockItem exists
        if stock_item is not None:
            # check if stockItem ids contains underscore
            stock_item = stock_item.find('typ:stockItem', namespaces)
            stock_item_ids = stock_item.find('typ:ids', namespaces)
            if stock_item_ids is not None and '_' in stock_item_ids.text:
                
                # split stockItem ids by underscore
                stock_item_ids_text = stock_item_ids.text.split('_')
                home_currency = inv_item.find('inv:homeCurrency', namespaces)
                foreign_currency = inv_item.find('inv:foreignCurrency', namespaces)
                quantity = inv_item.find('inv:quantity', namespaces)
                invoice = inv_item.getparent()
                delete_element(inv_item.getparent(), inv_item)
                
                for stock_item_id in stock_item_ids_text:
                    # find stockItem in XML feed by prodcut_id
                    product_obj = next((item for item in xml_feed if item['PRODUCT_CODE'] == stock_item_id), None)
                    # create new invoiceItem
                    if product_obj is not None:
                        price_vat = float(product_obj['PRICE_VAT']) - float(product_obj['PRICE'])
                        if home_currency is not None:
                            # create new invoiceItem in home currency
                            item_data = {
                                'text': product_obj['PRODUCT'],
                                'quantity': quantity.text,
                                'unit': 'ks',
                                'payVAT': False,
                                'rateVAT': vat_rate.get(str(product_obj['VAT']), 'high'),
                                'unitPrice': float(product_obj['PRICE_VAT']),
                                'price': float(product_obj['PRICE']),
                                'priceVAT': float(product_obj['PRICE_VAT']) - float(product_obj['PRICE']),
                                'stockItemId': stock_item_id,
                                'code': stock_item_id
                            }
                            new_inv_el = create_invoice_item_home_currency(root, item_data)
                            
                            # add new invoinceItem to invoice

                        elif foreign_currency is not None:
                            exchange_rate = float(eur_rate)
                            unit_price = round(float(product_obj['PRICE_VAT']) / exchange_rate, 2)
                            price = round(float(product_obj['PRICE']) / exchange_rate, 2)
                            price_vat = round((float(product_obj['PRICE_VAT']) - float(product_obj['PRICE']))/ exchange_rate,2)
                            item_data = {
                                'text': product_obj['PRODUCT'],
                                'quantity': quantity.text,
                                'unit': 'ks',
                                'payVAT': False,
                                'rateVAT': vat_rate.get(str(product_obj['VAT']), 'high'),
                                'unitPrice': unit_price,
                                'price': price,
                                'priceVAT': price_vat,
                                'stockItemId': stock_item_id,
                                'code': stock_item_id
                            }
                            # create new invoiceItem in foreign currency
                            new_inv_el = create_invoice_item_foreign_currency(root, item_data)
                            
                        invoice.append(new_inv_el)


    
    # Process invoice items in home currency
    # and update unitPrice accordingly
    # This is the main part of the function
    # It finds all invoice items and updates their unitPrice
    # based on the price and priceVAT
    # It also sets payVAT to true
    # if the unitPrice is updated
    for invoice_item in root.findall('.//inv:invoiceItem', namespaces):
        home_currency = invoice_item.find('inv:homeCurrency', namespaces)
        foreign_currency = invoice_item.find('inv:foreignCurrency', namespaces)
        if home_currency is not None:
            price_elem = home_currency.find('typ:price', namespaces)
            price_vat_elem = home_currency.find('typ:priceVAT', namespaces)
            unit_price_elem = home_currency.find('typ:unitPrice', namespaces)
            pay_vat_elem = invoice_item.find('inv:payVAT', namespaces)
            
            if all([price_elem is not None, price_vat_elem is not None, unit_price_elem is not None]):
                try:
                    price = float(price_elem.text)
                    price_vat = float(price_vat_elem.text)
                    new_unit_price = price + price_vat
                    unit_price_elem.text = f"{new_unit_price:.2f}"
                    pay_vat_elem.text = 'true'
                except (ValueError, TypeError) as e:
                    print(f"Error processing prices: {e}")

        # Process foreign currency if it exists
        # and update unitPrice accordingly
        # This is similar to the home currency processing but for foreign currency
        if foreign_currency is not None:
            price_elem = foreign_currency.find('typ:price', namespaces)
            price_vat_elem = foreign_currency.find('typ:priceVAT', namespaces)
            unit_price_elem = foreign_currency.find('typ:unitPrice', namespaces)
            pay_vat_elem = invoice_item.find('inv:payVAT', namespaces)
            
            if all([price_elem is not None, price_vat_elem is not None, unit_price_elem is not None]):
                try:
                    price = float(price_elem.text)
                    price_vat = float(price_vat_elem.text)
                    new_unit_price = price + price_vat
                    unit_price_elem.text = f"{new_unit_price:.2f}"
                    pay_vat_elem.text = 'true'
                except (ValueError, TypeError) as e:
                    print(f"Error processing prices: {e}")

        # add store subelement to stockItem
        stock_item = invoice_item.find('inv:stockItem', namespaces)

        if stock_item is not None and store_id is not None:
            # Add store subelement to stockItem and set its value
            store_elem = add_element(stock_item, 'typ:store')
            add_element(store_elem, 'typ:ids', store_id)

    # Update invoice header with bank details
    # and symConst if provided
    # Only if the currency is EUR
    for invoice in root.findall('.//inv:invoice', namespaces):
        invoice_header = invoice.find('inv:invoiceHeader', namespaces)
        invoice_summary = invoice.find('inv:invoiceSummary', namespaces)
        if invoice_summary is not None:
            currency_id_elem = invoice_summary.find('inv:foreignCurrency/typ:currency/typ:ids', namespaces)
            if currency_id_elem is not None and currency_id_elem.text == 'EUR':
                if bank_id is not None:
                    account_elem = add_element(invoice_header, 'inv:account')
                    add_element(account_elem, 'typ:ids', bank_id)
                    add_element(account_elem, 'typ:accountNo', account_no)
                    add_element(account_elem, 'typ:bankCode', bank_code)
                    if const_symbol is not None:
                        add_element(invoice_header, 'inv:symConst', const_symbol)

def process_orders_xml(xml_data, bank_id, account_no, bank_code, const_symbol, store_id, feed_url, hash, eur_rate):
    """
    Edit XML data and return modified XML as string
    
    Args:
        xml_data (str/bytes): Input XML data
        bank_id (str): Bank ID
        account_no (str): Account number
        bank_code (str): Bank code
        const_symbol (str): Symbol constant
        store_id (str): Store ID
        feed_url (str): URL of the XML feed
        hash (str): Hash for authentication
        eur_rate (float): EUR exchange rate
        
    Returns:
        str: Modified XML data as string
    """
    tree = parse_xml_to_etree(xml_data)
    if tree is None:
        return None
        
    root = tree
    update_unit_prices(root, bank_id, account_no, bank_code, const_symbol, store_id, feed_url, hash, eur_rate)
    
    return etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True).decode('utf-8')


import lxml
import xmltodict
import json


def parse_receipt_xml(xml_string: str) -> dict:
    """
    Parse the XML string into a dictionary.

    Args:
        xml_string (str): The XML string to parse.

    Returns:
        dict: The parsed XML as a dictionary.
    """
    try:
        # Parse the XML string into an ElementTree object
        xml_dict = xmltodict.parse(xml_string)
        parsed_dict = xml_dict['dat:dataPack']['dat:dataPackItem']['pri:prijemka']['pri:prijemkaDetail']
        receipt_items = parsed_dict['pri:prijemkaItem']
        return receipt_items
    except Exception as e:
        raise ValueError(f"Error parsing XML: {e}") from e
    
def create_receipt_xml(receipt_items: dict) -> str:
    """
    Create an XML string from the receipt items dictionary.

    Example XML structure:
    <SHOP>
        <SHOPITEM>
            <CODE>12345</CODE> - product code
            <NAME>Produkt 1</NAME> - prouct name
            <STOCK>
                <AMOUNT>8</AMOUNT>
            </STOCK>
        </SHOPITEM>
        <SHOPITEM>
            <CODE>67890</CODE>
            <NAME>Produkt 2</NAME>
            <STOCK>
                <AMOUNT>5</AMOUNT>
            </STOCK>
        </SHOPITEM>
    </SHOP>

    Args:
        receipt_items (dict): The receipt items dictionary.

    Returns:
        str: The generated XML string.
    """

    try:
        # Create the XML structure
        xml_dict = {
            'SHOP': {
                'SHOPITEM': []
            }
        }
        for item in receipt_items:
            shop_item = {
                'CODE': item['pri:code'],
                'NAME': item['pri:text'],
                'STOCK': {
                    'AMOUNT': item['pri:quantity']
                }
            }
            xml_dict['SHOP']['SHOPITEM'].append(shop_item)

        # Convert the dictionary to an XML string
        xml_string = xmltodict.unparse(xml_dict, pretty=True)
        return xml_string
    except Exception as e:
        raise ValueError(f"Error creating XML: {e}") from e


