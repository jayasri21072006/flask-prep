import pandas as pd
import xml.etree.ElementTree as ET
from config import CSV_FILE, EXCEL_FILE, XML_FILE


def convert_to_csv(df):
    df.to_csv(CSV_FILE, index=False)
    return CSV_FILE


def convert_to_excel(df):
    df.to_excel(EXCEL_FILE, index=False)
    return EXCEL_FILE


def convert_to_xml(df):
    root = ET.Element("WeatherData")
    for _, row in df.iterrows():
        entry = ET.SubElement(root, "Entry")
        for col in df.columns:
            child = ET.SubElement(entry, col)
            child.text = str(row[col])
    tree = ET.ElementTree(root)
    tree.write(XML_FILE)
    return XML_FILE
