# Module to load S&P500 data

import pandas as pd

from typing import Union, List, Dict

# main loading source for s&p500 company list
url='https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

def load() -> pd.DataFrame:
    return pd.DataFrame(pd.read_html(url, header=0)[0])

def security_list(return_type: str = "list") -> Union[List, pd.Series]:
    '''
    Returns a list of S&P500 companies unless return_type == "series" or "s".

    :param return_type: set to 'list'. If a series should be returned, set to 'series' or 's'.

    **Examples**

    >>> sp_securities = security_list()
    >>> print(sp_securities)
    ['3M', 'A. O. Smith' ... 'Zebra Technologies', 'Zimmer Biomet', 'Zoetis']

    >>> security_list(return_type='series')
    0                       3M
    1              A. O. Smith
    2      Abbott Laboratories
    3                   AbbVie
    4                Accenture
              ...
    498             Xylem Inc.
    499            Yum! Brands
    500     Zebra Technologies
    501          Zimmer Biomet
    502                 Zoetis
    Name: Symbol, Length: 503, dtype: object
    '''
    s = load()['Security']
    if return_type.strip().lower()=="series" or return_type.strip().lower()=="s":
        return s
    return s.tolist()

def ticker_list(return_type: str = "list") -> Union[List, pd.Series]:
    '''
    Returns a list of S&P500 tickers unless return_type == "series" or "s".

    :param return_type: set to 'list'. If a series should be returned, set to 'series' or 's'.

    **Examples**
    
    >>> sp_tickers = ticker_list()
    >>> print(sp_tickers)
    ['MMM', 'AOS', 'ABT' ... 'ZBRA', 'ZBH', 'ZTS']

    >>> print(ticker_list(return_type='series'))
    0       MMM
    1       AOS
    2       ABT
    3      ABBV
    4       ACN
       ...
    498     XYL
    499     YUM
    500    ZBRA
    501     ZBH
    502     ZTS
    Name: Symbol, Length: 503, dtype: object
    '''
    s = load()['Symbol']
    if return_type.strip().lower()=="series" or return_type.strip().lower()=="s":
        return s
    return s.tolist()

def company_sector(return_type: str = "dict") -> Union[Dict, pd.DataFrame]:
    '''
    Returns a dictionary of companies' respective GICS sector -- key, value: {security (str): sector (str)}.

    :param return_type: set to 'dict'. If a data frame should be returned, set to 'dataframe' or 'df'.

    **Usage**

    Pulling all index companies of a particular index to plot market similarities. 

    **Examples**
    
    >>> sp_sectors = company_sector()
    >>> print(sp_sectors)
    {'3M': 'Industrials', 'A. O. Smith': 'Industrials', 'Abbott Laboratories': 'Health Care' ... 'Zimmer Biomet': 'Health Care', 'Zoetis': 'Health Care'}

    >>> print(company_sector(return_type='df'))
                    Security             GICS Sector
    0                     3M             Industrials
    1            A. O. Smith             Industrials
    2    Abbott Laboratories             Health Care
    3                 AbbVie             Health Care
    4              Accenture  Information Technology
    ..                   ...                     ...
    498           Xylem Inc.             Industrials
    499          Yum! Brands  Consumer Discretionary
    500   Zebra Technologies  Information Technology
    501        Zimmer Biomet             Health Care
    502               Zoetis             Health Care
    '''
    df = load()[['Security', 'GICS Sector']]
    if return_type.strip().lower()=="dataframe" or return_type.strip().lower()=="df":
        return df
    return {df['Security'][i]: df['GICS Sector'][i] for i in range(len(df))}

def company_industry(return_type: str = "dict") -> Union[Dict, pd.DataFrame]:
    '''
    Returns a dictionary of companies' respective GICS sub-industry -- key, value: {security (str): industry (str)}.

    :param return_type: set to 'dict'. If a data frame should be returned, set to 'dataframe' or 'df'.

    **Usage**

    Time series plotting with index companies from a particular sub-industry.

    **Examples**
    
    >>> sp_industries = company_industry()
    >>> print(sp_industries)
    {'3M': 'Industrial Conglomerates', 'A. O. Smith': 'Building Products', 'Abbott Laboratories': 'Health Care Equipment', 
    'AbbVie': 'Biotechnology' ... 'Zimmer Biomet': 'Health Care Equipment', 'Zoetis': 'Pharmaceuticals'}

    >>> print(company_industry(return_type='df'))
                    Security                             GICS Sub-Industry
    0                     3M                      Industrial Conglomerates
    1            A. O. Smith                             Building Products
    2    Abbott Laboratories                         Health Care Equipment
    3                 AbbVie                                 Biotechnology
    4              Accenture                IT Consulting & Other Services
    ..                   ...                                           ...
    498           Xylem Inc.  Industrial Machinery & Supplies & Components
    499          Yum! Brands                                   Restaurants
    500   Zebra Technologies            Electronic Equipment & Instruments
    501        Zimmer Biomet                         Health Care Equipment
    502               Zoetis                               Pharmaceuticals

    [503 rows x 2 columns]
    '''
    df = load()[['Security', 'GICS Sub-Industry']]
    if return_type.strip().lower()=="dataframe" or return_type.strip().lower()=="df":
        return df
    return {df['Security'][i]: df['GICS Sub-Industry'][i] for i in range(len(df))}
    
def get_securities_by_sector(sector: str, ticker_display: bool = True, return_type: str = "list") -> Union[List, pd.Series]:
    '''
    Return a list of securities as their respective tickers that belong to a specified sector.
    '''