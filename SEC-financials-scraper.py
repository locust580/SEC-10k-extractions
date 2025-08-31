from lxml import etree
import os
import pandas as pd

xbrl_tags_income = {
    #Revenues
    'Revenue': ['RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues'],
    'CoGS': ['CostOfGoodsAndServicesSold', 'CostOfRevenue'],
    'Gross Profit': ['GrossProfit'],
    
    #Operating Expenses
    'R&D': ['ResearchAndDevelopmentExpense'],
    'SG&A': ['SellingGeneralAndAdministrativeExpense'],
    'Total Operating Expenses': ['OperatingExpenses'],

    #Total income after operating expenses taken out
    'Income from Operations': ['OperatingIncomeLoss'],

    #D/A Expenses
    'Depreciation': ['Depreciation'],
    'Amortization': ['AmortizationOfIntangibleAssets'],

    #Interests
    'Interest Income': ['InvestmentIncomeInterest'],
    'Interest Expense (Negative)': ['InterestExpense', 'InterestExpenseNonoperating'],
    'Other Net': ['OtherNonoperatingIncomeExpense'],
    'Other Income/Expense Net': ['NonoperatingIncomeExpense'],

    #Final incomes
    'Income Before Tax': ['IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest'],
    'Income Tax': ['IncomeTaxExpenseBenefit'],
    'Net Income': ['NetIncomeLoss']
}

xbrl_tags_balance = {
    # Assets
    # Current assets:
        'Cash and cash equivalents': ["CashAndCashEquivalentsAtCarryingValue"],
        'Marketable securities': ["MarketableSecuritiesCurrent"],
        'Accounts receivable (net)': ["AccountsReceivableNetCurrent"],
        'Inventories': ["InventoryNet"],
        'Prepaid expenses and other current assets': ["PrepaidExpenseAndOtherAssetsCurrent"],
    'Total current assets': ["AssetsCurrent"],

    # Non-Current Assets:
    'Property and equipment (net)': ["PropertyPlantAndEquipmentNet"],
    'Operating lease assets': ["OperatingLeaseRightOfUseAsset"],
    'Goodwill': ["Goodwill"],
    'Intangible assets (net)': ["IntangibleAssetsNetExcludingGoodwill"],
    'Deferred income tax assets': ["DeferredIncomeTaxAssetsNet"],
    'Other assets': ["OtherAssetsNoncurrent"],
    
    'Total assets': ["Assets"],

    # Liabilities and Shareholders' Equity
    # Current liabilities:
        'Accounts payable': ["AccountsPayableCurrent"],
        'Accrued and other current liabilities': ["AccruedLiabilitiesCurrent"],
        'Short-term debt': ["DebtCurrent"],
    'Total current liabilities': ["LiabilitiesCurrent"],

    # Non-Current Liabilities:
    'Long-term debt': ["LongTermDebtNoncurrent"],
    'Long-term operating lease liabilities': ["OperatingLeaseLiabilityNoncurrent"],
    'Other long-term liabilities': ["OtherLiabilitiesNoncurrent"],
    
    'Total liabilities': ["Liabilities"],

    'Total shareholders equity': ["StockholdersEquity"],
    'Total liabilities and shareholders equity': ["LiabilitiesAndStockholdersEquity"]
}

xbrl_tags_cashflow = {
    #Cash flows from operating activities:
    'Net Income': [],
    #Adjustments to reconcile net income to net cash provided by operating activities:
        'Stock-based compensation expense': [],
}

folder = "10k_xml_files"
xml_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".xml")]
file_dates = []
csv_data = []
file_index = 0

usr_input = input("""
1 for Statement of Income
2 for Balance Sheets
3 for Cash Flows
Input: """)

def findDate(root, date, elem):
    cref = elem.get("contextRef")
    crefElement = root.xpath(f"//*[@id='{cref}']")[0]
    
    if len(crefElement.xpath(".//*[local-name()='instant']")) != 0:
        foundDate = crefElement.xpath(".//*[local-name()='instant']")[0].text.strip()
    elif len(crefElement.xpath(".//*[local-name()='endDate']")) != 0:
        foundDate = crefElement.xpath(".//*[local-name()='endDate']")[0].text.strip()
    
    if foundDate == date.text.strip():
        return True
    else:
        return False

#Income from operations always needs double-checking
def statementIncome(root, date, file_index):
    for item in xbrl_tags_income:
        for tag in xbrl_tags_income[item]:
            elems = root.xpath(f"//*[local-name()='{tag}']")  # searches entire tree, returns list of elements with the given tag in it
            if len(elems) != 0:
                properDateMaxValue = max([int(float(e.text.strip())) for e in elems if findDate(root, date, e) == True])
                #properDateMaxValue = properDateMaxValue / 1000000
                try:
                    csv_data[file_index][item] = properDateMaxValue
                except Exception as e:
                    print(f"Error: {e}")

def balanceSheet(root, date, file_index):
    for item in xbrl_tags_balance:
        for tag in xbrl_tags_balance[item]:
            elems = root.xpath(f"//*[local-name()='{tag}']")  # searches entire tree, returns list of elements with the given tag in it
            if len(elems) != 0:
                properDateMaxValue = max([int(float(e.text.strip())) for e in elems if findDate(root, date, e) == True])
                #dislike millions? uncomment below!
                #properDateMaxValue = properDateMaxValue / 1000000
                try:
                    csv_data[file_index][item] = properDateMaxValue
                except Exception as e:
                    print(f"Error: {e}")
    

def cashFlows():
    print("r")

for file in sorted(xml_files):
    xmltree = etree.parse(file) # parses file into xml tree
    root = xmltree.getroot() # finds topmost element in the tree to pass queries on

    date = root.xpath("//*[local-name()='endDate']")[0] # store file date
    
    file_dates.append(date.text.strip()) # add file date to file_dates list
    csv_data.append({"Year": date.text.strip()[0:4]}) # appends each year's dictionary to data list, later turned into a csv pivoting around year

    if usr_input == "1":
        statementIncome(root, date, file_index)
    elif usr_input == "2":
        balanceSheet(root, date, file_index)
    elif usr_input == "3":
        cashFlows
    else:
        print("Cmon man that's not a correct input")
        break

    file_index += 1



csv_file = pd.DataFrame(csv_data).set_index("Year").T
print(csv_file)
companyString = xml_files[0][len(folder)+1:len(folder)+5]
if usr_input == "1":
    csv_file.to_csv(f"isttmnts-{companyString}-{file_dates[0]}-{file_dates[len(file_dates)-1]}.csv")
elif usr_input == "2":
    csv_file.to_csv(f"bsttmnts-{companyString}-{file_dates[0]}-{file_dates[len(file_dates)-1]}.csv")
elif usr_input == "3":
    csv_file.to_csv(f"csttmnts-{companyString}-{file_dates[0]}-{file_dates[len(file_dates)-1]}.csv")


