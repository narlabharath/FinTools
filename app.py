# -*- coding: utf-8 -*-
"""
Created on Thu Jun 24 19:14:50 2021

@author: narla
"""
import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
plt.style.use('ggplot')
plt.rcParams['figure.dpi'] = 300
import streamlit as st
#st.set_page_config(layout="wide")

st.markdown("<h1 style='text-align: center; color: blue;'\
    >Savings Vs Post Retirement Expenses Estimator</h1>", unsafe_allow_html=True)

st.subheader('Input parameters:')

col1, col2, col3 = st.beta_columns(3)
CurrentIncome = float(col1.text_input("Current Income (PerMonth):", 200000))
CurrentMonthlyExpensesPct = float(col2.text_input("Monthly Expenses (PctOfIncome):", 70))
IncomeGrowthRate = float(col3.text_input("Expected Yearly Income Growth Rate:", 10))

col3, col4, col5 = st.beta_columns(3)
CurrentAge = float(col3.text_input("Current Age:", 31))
RetirementAge = float(col4.text_input("Expected Retirement Age:", 45))
LifeExpectancy = float(col5.text_input("Expected Life Expectancy:", 70))

col6, col7, col8 = st.beta_columns(3)
InflationRate = float(col6.text_input("Expected Inflation rate for Expenses:", 7))
TaxRate = float(col7.text_input("Expected Tax rate for Withdrawls:", 10))
InvestmentGrowthRate = float(col8.text_input("Expected Return on Savings:", 10))


InitialSavings = float(st.text_input("Current Savings:", 350000))

st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

Retired = st.radio('Currently Retired',['Yes','No'],index=1)
if Retired == 'Yes':
    Retired = True
    CurrentExpensesIfRetired = float(st.text_input("Current Expenses PerMonth:", 40000))
else:
  Retired = False  
ActualExpensesStartInFuture  = st.radio('Expecting Increased expenses in future',['Yes','No'],index=1)
if ActualExpensesStartInFuture == 'Yes':
    ActualExpensesStartInFuture = True
    col9, col10 = st.beta_columns(2)
    ActualExpensesStartAge = float(col9.text_input("Age from where the expenses would increase:", 37))
    PresentValueOfActualExpenses = float(col10.text_input("Present value of increased expenses:", 60000))
else:
    ActualExpensesStartInFuture = False
    ActualExpensesStartAge = CurrentAge
    PresentValueOfActualExpenses = 0
UsePeakMonthlyIncome  = st.radio('Expecting peak in income growth rate',['Yes','No'],index=0)
if UsePeakMonthlyIncome == 'Yes':
    UsePeakMonthlyIncome = True
    col10, col11 = st.beta_columns(2)
    MonthlyPeakVal = float(col10.text_input("Expected Monthly income at which peak:", 600000))
    GrowthAfterPeak = float(col11.text_input("Expected Yearly income growth rate after peak:", 3))
else:
    UsePeakMonthlyIncome = False

if st.button('Show Estimations'):

    TotalMonths = pd.date_range(datetime.now().date(),periods=(LifeExpectancy-CurrentAge)*12,
                                 freq='M')

    OrigCurrentAge = CurrentAge
    CurrentMonthlyExpensesPct = CurrentMonthlyExpensesPct / 100
    IncomeGrowthRate = IncomeGrowthRate / 100
    InflationRate = InflationRate / 100
    TaxRate = TaxRate / 100
    InvestmentGrowthRate = InvestmentGrowthRate / 100
    InvestmentGrowthRate_Month = ((1+InvestmentGrowthRate) ** (1/12)) - 1
    GrowthAfterPeak = GrowthAfterPeak / 100

    CurrentInflation = 1
    CurrentIncomeGrowth = 1
    CurrentSavingsGrowth = 1
    CumulativeSavings = InitialSavings
    if Retired:
        CurrentExpenses = CurrentExpensesIfRetired
    else:
        CurrentExpenses = CurrentIncome * CurrentMonthlyExpensesPct

    AllMonthsDetails = pd.DataFrame()
    for i in range(len(TotalMonths)):
        # break
        if ((i+1) % 12) == 0:
            CurrentAge += 1
            CurrentIncome = CurrentIncome * (1+(IncomeGrowthRate))
            if (UsePeakMonthlyIncome) & (CurrentIncome>=MonthlyPeakVal):
                IncomeGrowthRate = GrowthAfterPeak 
            CurrentExpenses = CurrentExpenses * (1 + (InflationRate))
            PresentValueOfActualExpenses = PresentValueOfActualExpenses * (1 + (InflationRate))
            CurrentExpensesIfRetired = CurrentExpensesIfRetired * (1 + (InflationRate))
        
        if CurrentAge > RetirementAge:
            Retired = True
        
        if not Retired:
            if (ActualExpensesStartInFuture) & (CurrentAge>=ActualExpensesStartAge):
                CurrentExpenses = PresentValueOfActualExpenses
                CurrentSavings = CurrentIncome - CurrentExpenses    
            if (not ActualExpensesStartInFuture) | (CurrentAge<ActualExpensesStartAge):
                CurrentSavings = CurrentIncome - CurrentExpenses
            CurrentExpensesIfRetired = CurrentExpenses
        else:
            CurrentIncome = 0
            CurrentExpenses = 0
            CurrentSavings = 0
        
        ExpensesWithdrawl = 0
        TaxOnExpensesWithdrawl = 0
        if Retired:
            ExpensesWithdrawl = CurrentExpensesIfRetired
            TaxOnExpensesWithdrawl = (ExpensesWithdrawl / (1-TaxRate)) - ExpensesWithdrawl
        
        OpeningSavings = CumulativeSavings
        RetEarnedOnSavings = CumulativeSavings * InvestmentGrowthRate_Month
        AddSavings = CurrentSavings
        CloseSavings = OpeningSavings + AddSavings + RetEarnedOnSavings - ExpensesWithdrawl - TaxOnExpensesWithdrawl
        CumulativeSavings = CloseSavings
        
        CurrentDetails = pd.DataFrame([[CurrentAge,CurrentIncome,CurrentExpenses,CurrentSavings,
                      ExpensesWithdrawl,TaxOnExpensesWithdrawl,OpeningSavings,RetEarnedOnSavings,CloseSavings]],
                     index = [TotalMonths[i]])
        CurrentDetails.columns = ['CurrentAge','CurrentIncome','CurrentExpenses','CurrentSavings',
                      'ExpensesWithdrawl','TaxOnExpensesWithdrawl','OpeningSavings','RetEarnedOnSavings','CloseSavings']
        AllMonthsDetails = pd.concat([AllMonthsDetails,CurrentDetails])
        
        if CumulativeSavings < 0:
            st.markdown("<h3 style='text-align: center; color: red;'\
    >You cannot financially survive beyond age: {}</h3>".format(CurrentAge), unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; color: blue;'>Try Changing some parameters</h3>", unsafe_allow_html=True)
            #st.markdown('You cannot financially survive beyond age: {}\nTry Changing some parameters'.format(CurrentAge))
            break
        
    AllMonthsDetails = AllMonthsDetails.replace(0,np.nan)

    def date2yday(x):
        """Convert matplotlib datenum to days since 2018-01-01."""
        y = ((x - mdates.date2num(datetime.now().date())) / 365) + OrigCurrentAge
        return y
    def yday2date(x):
        """Return a matplotlib datenum for *x* days after 2018-01-01."""
        y = x + mdates.date2num(datetime.now().date())
        return y

    EarningYears = AllMonthsDetails[['CurrentAge','CurrentIncome', 'CurrentExpenses', 'CurrentSavings']].copy()
    EarningYears.reset_index(inplace=True)
    EarningYears.set_index(['index','CurrentAge'],inplace=True)
    EarningYears.dropna(inplace=True)
    if not EarningYears.empty:
        EarningYears = (EarningYears / 100000)
        EarningYears.reset_index(inplace=True)
        fig1, ax = plt.subplots()
        for Col in ['CurrentIncome', 'CurrentExpenses', 'CurrentSavings']:
            ax.plot('index',Col,data = EarningYears)
        secax_x = ax.secondary_xaxis('top', functions=(date2yday, yday2date))
        secax_x.set_xlabel('Age')
        plt.title('Monthly Contribution during earning years\n(In Lakhs)')
        plt.legend(['CurrentIncome', 'CurrentExpenses', 'CurrentSavings'])
        #plt.show()
        #st.pyplot(fig1)

    WithdrawlYears = AllMonthsDetails[['CurrentAge','ExpensesWithdrawl','RetEarnedOnSavings']].copy()
    WithdrawlYears.reset_index(inplace=True)
    WithdrawlYears.set_index(['index','CurrentAge'],inplace=True)
    WithdrawlYears.dropna(inplace=True)
    if not WithdrawlYears.empty:
        WithdrawlYears = (WithdrawlYears / 100000)
        WithdrawlYears.reset_index(inplace=True)
        fig2, ax = plt.subplots()
        for Col in ['ExpensesWithdrawl','RetEarnedOnSavings']:
            ax.plot('index',Col,data = WithdrawlYears)
        secax_x = ax.secondary_xaxis('top', functions=(date2yday, yday2date))
        secax_x.set_xlabel('Age')
        plt.title('Monthly Withdrawl & Returns on savings \nduring retirement years (In Lakhs)')
        plt.legend(['ExpensesWithdrawl','RetEarnedOnSavings'])
        #plt.show()
        #st.pyplot(plt)

    if not EarningYears.empty:
        OverallMonthlyDetails = AllMonthsDetails[['CurrentAge','CurrentIncome', 'CurrentExpenses', 'CurrentSavings',
                                                'ExpensesWithdrawl']].copy()
        OverallMonthlyDetails.reset_index(inplace=True)
        OverallMonthlyDetails.set_index(['index','CurrentAge'],inplace=True)
        OverallMonthlyDetails = OverallMonthlyDetails/100000
        OverallMonthlyDetails.reset_index(inplace=True)
        fig3, ax = plt.subplots()
        for Col in ['CurrentIncome', 'CurrentExpenses', 'CurrentSavings','ExpensesWithdrawl']:
            ax.plot('index',Col,data = OverallMonthlyDetails)
        secax_x = ax.secondary_xaxis('top', functions=(date2yday, yday2date))
        secax_x.set_xlabel('Age') 
        plt.title('Overall Monthly details\n(In Lakhs)')
        plt.legend(['CurrentIncome', 'CurrentExpenses', 'CurrentSavings','ExpensesWithdrawl'])
        #plt.show()
        #st.pyplot(plt)

    RetEarned = AllMonthsDetails[['CurrentAge','RetEarnedOnSavings']]
    RetEarned.reset_index(inplace=True)
    RetEarned.set_index(['index','CurrentAge'],inplace=True)
    RetEarned = (RetEarned/100000)
    RetEarned.reset_index(inplace=True)
    fig4, ax = plt.subplots()
    ax.plot('index','RetEarnedOnSavings',data = RetEarned)
    secax_x = ax.secondary_xaxis('top', functions=(date2yday, yday2date))
    secax_x.set_xlabel('Age') 
    plt.title('Monthly Returns on Savings\n(In Lakhs)')
    plt.legend(['RetEarnedOnSavings'])
    #plt.show()
    #st.pyplot(plt)

    SavingsDetails = AllMonthsDetails[['CurrentAge','CloseSavings']]
    SavingsDetails.reset_index(inplace=True)
    SavingsDetails.set_index(['index','CurrentAge'],inplace=True)
    SavingsDetails = (SavingsDetails/10000000)
    SavingsDetails.reset_index(inplace=True)
    fig5, ax = plt.subplots()
    ax.plot('index','CloseSavings',data = SavingsDetails)
    secax_x = ax.secondary_xaxis('top', functions=(date2yday, yday2date))
    secax_x.set_xlabel('Age') 
    plt.title('Overall Savings\n(In Crores)')
    plt.legend(['CloseSavings'])
    #plt.show()
    #st.pyplot(plt)
    if not EarningYears.empty:
        col12, col13 = st.beta_columns(2)
        col12.pyplot(fig1)
        col13.pyplot(fig3)

    col13, col14 = st.beta_columns(2)
    col13.pyplot(fig4)
    col14.pyplot(fig5)

    col15, col16 = st.beta_columns(2)
    col13.pyplot(fig2)






























































