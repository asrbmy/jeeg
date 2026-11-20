# Reference: Money and business

Calculators for loans, savings, tax, bills and splitting, your expense records and budgets, a lending ledger, a small stock list and invoices.

52 tasks. Each entry shows the **usage** (`<x>` you fill in, `[x]` optional), what the task does, how it behaves, other words that also find it, and the script file you can read or edit. Say the task name, or the usage with your words filled in. `explain <words>` shows how any phrase is matched; `<task> preview` or `--dry-run` shows what would happen without doing it.

Categories on this page: [money](#money)

## money

### add bill

**Usage:** `add bill <name> <day> [amount]`  
**What it does:** Remember a monthly bill's due day (add bill electricity 15 1200)  
**Also found by:** `bill reminder`, `monthly bill`, `due date bill`, `remember bill`, `recurring bill`, `save bill`  
**Your words:** passed through untouched  
**Script:** `scripts/add_bill.py`

### add expense

**Usage:** `add expense <amount> <category> [note]`  
**What it does:** Record spending (spent 450 on groceries, add expense 200 food lunch)  
**Also found by:** `expense`, `spent`, `paid`, `record expense`, `log expense`, `cost`  
**Your words:** passed through untouched  
**Script:** `scripts/add_expense.py`

### bank import

**Usage:** `import bank <file.csv>`  
**What it does:** Import a bank statement CSV into your expenses (import bank statement.csv); guesses categories, skips duplicates  
**Also found by:** `import bank`, `bank statement`, `bank csv`, `import statement`, `import transactions`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/bank_import.py`

### borrow money

**Usage:** `borrow <amount> from <name>`  
**What it does:** Note money you borrowed from someone (borrow 300 from asha)  
**Behaviour:** never saved in history.  
**Also found by:** `borrow`, `borrowed`, `i borrowed`, `i owe`, `took loan from`, `money borrowed`  
**Your words:** passed through untouched  
**Script:** `scripts/borrow_money.py`

### budget report

**Usage:** `budget report`  
**What it does:** Show this month's spending against your budgets (budget report)  
**Also found by:** `budgets`, `am i over budget`, `budget left`, `show budget`, `budget check`, `spending limits`  
**Script:** `scripts/budget_report.py`

### card dues

**Usage:** `add card <name> <date> | cards | remove card <name>`  
**What it does:** Track credit card payment due dates (add card visa 15 nov, cards, remove card visa)  
**Also found by:** `credit card due`, `card due`, `card payment due`, `add card`, `my cards`, `remove card`, `card bill date`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/card_dues.py`

### compound interest

**Usage:** `compound interest <amount> <rate%> <years>`  
**What it does:** Compound interest (compound interest 10000 7 3 years [monthly])  
**Also found by:** `interest`, `fd`, `fixed deposit`, `savings growth`, `deposit`, `ci`, `maturity`, `rd calculator`, `compounding`  
**Your words:** passed through untouched  
**Script:** `scripts/compound_interest.py`

### crypto price

**Usage:** `crypto price <coin>`  
**What it does:** Live cryptocurrency price (crypto price bitcoin) (needs internet)  
**Behaviour:** can use the internet.  
**Also found by:** `crypto`, `bitcoin`, `btc`, `ethereum`, `eth`, `cryptocurrency`, `coin price`, `dogecoin`, `solana`, `coin`  
**Your words:** passed through untouched  
**Script:** `scripts/crypto_price.py`

### currency convert

**Usage:** `currency <amount> <from> to <to>`  
**What it does:** Live currency conversion (currency 100 usd to inr) (needs internet)  
**Behaviour:** can use the internet.  
**Also found by:** `currency`, `exchange rate`, `forex`, `dollar`, `euro`, `rupee`, `usd`, `inr`, `convert currency`, `exchange`  
**Your words:** passed through untouched  
**Script:** `scripts/currency_convert.py`

### discount price

**Usage:** `discount <price> <percent> [more %]`  
**What it does:** Price after discount(s) (discount 2000 30% off, discount 2000 30 10)  
**Also found by:** `discount`, `sale`, `off`, `price after discount`, `final price`, `savings`, `offer price`, `percent off`, `markdown`, `coupon`  
**Your words:** passed through untouched  
**Script:** `scripts/discount_price.py`

### emi loan

**Usage:** `emi <amount> <rate%> <years>`  
**What it does:** Loan EMI (emi 5 lakh 8.5 5 years)  
**Also found by:** `emi`, `loan`, `home loan`, `car loan`, `personal loan`, `monthly payment`, `installment`, `instalment`, `interest rate`  
**Your words:** passed through untouched  
**Script:** `scripts/emi_loan.py`

### exchange rates

**Usage:** `exchange rates [base currency]`  
**What it does:** Table of today's exchange rates against the rupee (exchange rates, exchange rates eur)  
**Behaviour:** can use the internet.  
**Also found by:** `rupee rate`, `forex rates`, `dollar rate`, `currency rates`, `rupee vs dollar`, `usd to inr rate`, `today's rates`, `rate table`  
**Your words:** passed through untouched  
**Script:** `scripts/exchange_rates.py`

### expense total

**Usage:** `expense total [month]`  
**What it does:** Spending totals by category (expense total, expense total last month)  
**Also found by:** `total expenses`, `how much did i spend`, `spending summary`, `expense summary`, `monthly spending`, `budget summary`, `spending by category`  
**Your words:** passed through untouched  
**Script:** `scripts/expense_total.py`

### freelance rate

**Usage:** `freelance rate income <n> expenses <n> hours <n>`  
**What it does:** Work out the hourly rate you need (freelance rate income 4000 expenses 800 hours 25 weeks off 6).  
**Also found by:** `hourly rate`, `how much to charge`, `my hourly rate`, `rate calculator`, `consulting rate`, `charge per hour`, `day rate`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/freelance_rate.py`

### fuel cost

**Usage:** `fuel cost <km> km <mileage> kmpl <price>`  
**What it does:** Trip fuel cost from distance, mileage and price (fuel cost 250 km 18 kmpl 105 per litre)  
**Also found by:** `petrol cost`, `diesel cost`, `trip cost`, `mileage calculator`, `fuel calculator`, `how much petrol`, `travel cost`, `cost of trip`, `kmpl`  
**Your words:** passed through untouched  
**Script:** `scripts/fuel_cost.py`

### gst amount

**Usage:** `gst <amount> [rate] [inclusive]`  
**What it does:** GST add or remove (gst 1000 18, gst 1180 18 inclusive)  
**Also found by:** `gst`, `tax`, `vat`, `add gst`, `remove gst`, `gst inclusive`, `gst exclusive`, `cgst`, `sgst`, `igst`  
**Your words:** passed through untouched  
**Script:** `scripts/gst_amount.py`

### home meter

**Usage:** `meter add <name> <reading> | meter list <name> | meter use <name>`  
**What it does:** Log meter readings and see use per day (meter add electricity 12450, meter list electricity, meter use electricity)  
**Also found by:** `meter reading`, `electricity meter`, `water meter`, `gas meter`, `meter log`, `units used`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/home_meter.py`

### house split

**Usage:** `flat members <names> | flat add <what> <amount> paid by <name> [split <names>] | flat summary | flat clear`  
**What it does:** Share house costs between flatmates and see who pays whom (flat members amit ravi sam; flat add rent 18000 paid by amit; flat summary)  
**Behaviour:** never saved in history.  
**Also found by:** `flatmates`, `flat split`, `roommate expenses`, `who owes whom`, `housemates`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/house_split.py`

### hra exemption

**Usage:** `hra basic <amt> hra <amt> rent <amt> [metro]`  
**What it does:** HRA tax exemption (hra basic 50000 hra 20000 rent 18000 metro)  
**Also found by:** `hra`, `house rent allowance`, `hra calculator`, `rent exemption`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/hra_exemption.py`

### income tax

**Usage:** `income tax <income> [deductions <amount>]`  
**What it does:** Income tax, new vs old regime (income tax 12 lakh; income tax 18 lakh deductions 2 lakh)  
**Also found by:** `tax calculator`, `tax on salary`, `new regime`, `old regime`, `itr tax`, `how much tax`  
**Your words:** passed through untouched  
**Script:** `scripts/income_tax.py`

### interest tax

**Usage:** `interest tax <interest> tax <rate %>   |   interest tax deposit <amount> rate <%> tax <%>`  
**What it does:** Tax on interest earned (interest tax deposit 10000 rate 5 tax 25; interest tax 800 tax 15)  
**Also found by:** `tax on interest`, `savings interest tax`, `deposit interest tax`, `withholding tax interest`, `after tax interest`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/interest_tax.py`

### inventory

**Usage:** `stock add <item> <qty> [min <n>] | stock sell|remove <item> <qty> | stock set <item> <qty> | stock list | low stock | stock delete <item>`  
**What it does:** Keep a simple stock list for a shop or home (stock add rice 20 min 5, stock sell rice 3, stock list, low stock)  
**Also found by:** `stock count`, `shop stock`, `low stock`, `stock add`, `stock remove`, `items in stock`, `godown`, `store stock`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/inventory.py`

### lend money

**Usage:** `lend <amount> to <name> [note]`  
**What it does:** Note money you lent to someone (lend 500 to ravi for lunch)  
**Behaviour:** never saved in history.  
**Also found by:** `lend`, `lent`, `i lent`, `gave loan to`, `money lent`, `owes me`  
**Your words:** passed through untouched  
**Script:** `scripts/lend_money.py`

### loan compare

**Usage:** `compare loans <amt> <rate> <years> vs <rate> <years>`  
**What it does:** Compare two loan offers side by side (compare loans 500000 8.5% 5y vs 9% 4y).  
**Also found by:** `compare loans`, `loan comparison`, `compare emi`, `which loan is cheaper`, `two loans`, `loan offers`, `loan vs loan`, `compare loan offers`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/loan_compare.py`

### make invoice

**Usage:** `invoice <customer>: <qty> <item> at <rate>, ... [gst 18]`  
**What it does:** Make a simple GST invoice page (invoice Ravi Traders: 3 pens at 10, 2 books at 150 gst 18)  
**Also found by:** `invoice`, `create invoice`, `bill customer`, `gst invoice`, `tax invoice`, `generate invoice`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/make_invoice.py`

### mileage log

**Usage:** `mileage add <km> [note] | mileage report [month] | mileage rate <per km>`  
**What it does:** Log trips and work out what you can claim (mileage add 25 km office, mileage report, mileage rate 8)  
**Also found by:** `mileage`, `km log`, `trip log`, `distance log`, `mileage report`, `travel claim`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/mileage_log.py`

### monthly report

**Usage:** `monthly report [YYYY-MM]`  
**What it does:** Make a one-page report of this month (spending, budgets, recurring costs, mileage, 80C) you can open or print to PDF (monthly report)  
**Also found by:** `month report`, `money report`, `month summary page`, `report page`, `finance report`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/monthly_report.py`

### payment reminder

**Usage:** `payment reminder <name in your ledger | name amount [invoice X] [by date]>`  
**What it does:** Write a polite payment-reminder message and copy it (payment reminder ravi, or: payment reminder Ravi Traders 5000 invoice INV-0012 by 15 nov)  
**Behaviour:** never saved in history.  
**Also found by:** `remind to pay`, `dues reminder`, `unpaid reminder`, `polite reminder to pay`, `overdue reminder`, `invoice reminder`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/payment_reminder.py`

### percentage change

**Usage:** `percentage change <old> to <new>`  
**What it does:** Percentage change between two numbers (percentage change 80 to 100)  
**Also found by:** `percent change`, `increase`, `decrease`, `growth`, `how much percent`, `percent increase`, `percent decrease`, `change percent`, `difference percent`, `hike`  
**Your words:** passed through untouched  
**Script:** `scripts/percentage_change.py`

### ppf maturity

**Usage:** `ppf <amount a year> [years] [rate %]`  
**What it does:** PPF maturity (ppf 1.5 lakh a year; ppf 50000 a year 15 years)  
**Also found by:** `ppf`, `public provident fund`, `ppf calculator`, `ppf interest`  
**Your words:** passed through untouched  
**Script:** `scripts/ppf_maturity.py`

### profit margin

**Usage:** `profit margin cost <c> price <p>`  
**What it does:** Profit margin and markup, or the price you need for a target margin (profit margin cost 60 price 100 | price for 30% margin cost 70).  
**Also found by:** `margin`, `markup`, `gross margin`, `selling price for margin`, `price for margin`, `cost price margin`, `profit percentage`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/profit_margin.py`

### rd maturity

**Usage:** `rd <monthly amount> <rate %> <years>`  
**What it does:** Recurring deposit maturity (rd 5000 a month 6.5% 2 years)  
**Also found by:** `rd`, `recurring deposit`, `monthly deposit`, `post office rd`  
**Your words:** passed through untouched  
**Script:** `scripts/rd_maturity.py`

### recurring costs

**Usage:** `recurring add <amount> <name> [category] | recurring list | recurring apply | recurring remove <name>`  
**What it does:** Costs that repeat every month (recurring add 649 netflix entertainment, recurring list, recurring apply, recurring remove netflix)  
**Also found by:** `recurring`, `subscription`, `monthly cost`, `recurring expense`, `netflix monthly`, `rent monthly`, `subscriptions`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/recurring_costs.py`

### remove bill

**Usage:** `remove bill <name>`  
**What it does:** Delete a saved bill (remove bill electricity)  
**Also found by:** `delete bill`, `cancel bill`, `forget bill`, `stop bill reminder`  
**Your words:** passed through untouched  
**Script:** `scripts/remove_bill.py`

### remove budget

**Usage:** `remove budget <category>`  
**What it does:** Remove a category budget (remove budget food)  
**Also found by:** `delete budget`, `clear budget`, `drop budget`  
**Your words:** passed through untouched  
**Script:** `scripts/remove_budget.py`

### salary breakup

**Usage:** `salary breakup <amount> [a month|a year] [tax %] [pension %] [insurance %] [other <amount>]`  
**What it does:** Take-home pay from gross salary (salary breakup 5000 a month tax 20 pension 5; salary 60000 a year tax 22)  
**Also found by:** `take home pay`, `net salary`, `in hand salary`, `gross to net`, `salary after tax`, `paycheck`  
**Your words:** passed through untouched  
**Script:** `scripts/salary_breakup.py`

### set budget

**Usage:** `set budget <category> <amount>`  
**What it does:** Set a monthly spending limit for a category (set budget food 5000)  
**Also found by:** `budget for`, `monthly budget`, `spending limit`, `limit spending`, `budget limit`  
**Your words:** passed through untouched  
**Script:** `scripts/set_budget.py`

### settle ledger

**Usage:** `settle <name> [amount]`  
**What it does:** Mark a debt as paid (settle ravi, settle ravi 200 for a part payment)  
**Behaviour:** never saved in history.  
**Also found by:** `settle`, `settle up`, `settled`, `repaid`, `clear debt`, `debt cleared`, `clear ledger`  
**Your words:** passed through untouched  
**Script:** `scripts/settle_ledger.py`

### severance pay

**Usage:** `severance <years> years salary <amount> [a year] [weeks <n>]`  
**What it does:** Estimate severance or end-of-service pay (severance 5 years salary 4000 a month weeks 2)  
**Also found by:** `severance`, `end of service`, `gratuity`, `redundancy pay`, `termination pay`, `leaving bonus`  
**Your words:** passed through untouched  
**Script:** `scripts/severance_pay.py`

### show expenses

**Usage:** `show expenses [category] [month]`  
**What it does:** List expenses (show expenses, show expenses food, show expenses last month)  
**Also found by:** `list expenses`, `my expenses`, `spending list`, `expense list`, `expense history`, `where did i spend`  
**Your words:** passed through untouched  
**Script:** `scripts/show_expenses.py`

### show ledger

**Usage:** `ledger [name]`  
**What it does:** See who owes you and who you owe (ledger, who owes me, show ledger ravi)  
**Behaviour:** never saved in history.  
**Also found by:** `ledger`, `who owes`, `who owes me`, `who do i owe`, `money owed`, `dues list`, `balances`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/show_ledger.py`

### sip goal

**Usage:** `sip goal <amount> in <years> years [at <rate>%]`  
**What it does:** Monthly saving needed to reach a goal (sip goal 1 million in 15 years at 8%; how much to save for 50000 in 3 years)  
**Also found by:** `savings goal`, `how much to save`, `monthly investment needed`, `how much sip`  
**Your words:** passed through untouched  
**Script:** `scripts/sip_goal.py`

### sip growth

**Usage:** `sip <monthly> <return%> <years>`  
**What it does:** SIP growth (sip 5000 12 10 years: monthly amount, yearly return %, years)  
**Also found by:** `sip`, `mutual fund`, `systematic investment`, `investment growth`, `invest monthly`, `returns`, `wealth`, `retirement corpus`, `monthly investment`  
**Your words:** passed through untouched  
**Script:** `scripts/sip_growth.py`

### spending anomalies

**Usage:** `spending anomalies`  
**What it does:** Find unusually large or possibly duplicated expenses (spending anomalies).  
**Also found by:** `unusual expenses`, `odd spending`, `duplicate expenses`, `expense outliers`, `unusual spending`, `suspicious expenses`, `spending check`  
**Script:** `scripts/spending_anomalies.py`

### spending forecast

**Usage:** `spending forecast`  
**What it does:** Predict this month's total spending from your pace so far, against your budgets (spending forecast).  
**Also found by:** `expense forecast`, `will i overspend`, `month end spending`, `projected spending`, `predict spending`, `budget forecast`, `end of month spending`  
**Script:** `scripts/spending_forecast.py`

### spending trends

**Usage:** `spending trends`  
**What it does:** Month-by-month spending, and which categories grew or shrank (spending trends).  
**Also found by:** `expense trends`, `spending history`, `monthly spending`, `spending over time`, `where is my money going`, `spending comparison`, `expenses by month`  
**Script:** `scripts/spending_trends.py`

### split bill

**Usage:** `split bill <amount> among <n> [tip %]`  
**What it does:** Split a bill (split bill 2400 among 4 tip 10%)  
**Also found by:** `split`, `bill`, `share`, `divide bill`, `per person`, `restaurant bill`, `tip`, `dutch`, `split the cost`, `each person pays`  
**Your words:** passed through untouched  
**Script:** `scripts/split_bill.py`

### tax saving

**Usage:** `80c add <amount> <what> | 80c | 80c remove <what>`  
**What it does:** Track your Section 80C investments against the 1,50,000 limit (80c add 50000 ppf, 80c, 80c remove ppf)  
**Also found by:** `80c`, `tax saving investments`, `section 80c`, `ppf elss`, `tax deduction`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/tax_saving.py`

### tip calculator

**Usage:** `tip <bill> [percent%] [split <people>]`  
**What it does:** Work out a tip and split the bill (tip 1200 10%, tip 2450 12% split 4)  
**Also found by:** `tip`, `calculate tip`, `how much tip`, `service charge`, `bill with tip`, `tip percentage`, `gratuity`  
**Your words:** passed through untouched  
**Script:** `scripts/tip_calculator.py`

### undo expense

**What it does:** Remove the last recorded expense  
**Behaviour:** asks before running.  
**Also found by:** `delete last expense`, `remove last expense`, `wrong expense`, `mistake expense`, `remove expense`  
**Script:** `scripts/undo_expense.py`

### unit price

**Usage:** `unit price <qty><unit> <price> vs <qty><unit> <price>`  
**What it does:** Which pack is cheaper per kg or litre (unit price 500g 45 vs 1kg 80)  
**Also found by:** `which is cheaper`, `price per kg`, `price per litre`, `compare prices`, `better deal`, `cheaper pack`, `best value`, `price per 100g`, `compare packs`  
**Your words:** passed through untouched  
**Script:** `scripts/unit_price.py`

### upcoming bills

**Usage:** `upcoming bills [days]`  
**What it does:** Bills due soon (upcoming bills, upcoming bills 30)  
**Also found by:** `bills due`, `what bills are due`, `show bills`, `due this week`, `my bills`, `pending bills`, `list bills`, `bills this month`  
**Your words:** passed through untouched  
**Script:** `scripts/upcoming_bills.py`


Back to [Home](Home) | [Task Catalog](Task-Catalog).
