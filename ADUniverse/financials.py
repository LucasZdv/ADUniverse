import constant as C
import numpy as np

# CHANGED: added keyword parameters and documentation for function


def loan_calculator(loan, feature = 0, apr=C.MONTHLY_APR, maturity=C.ANNUAL_MATURITY):
    """
    Calculates the monthly payments for a loan over
    the maturity period.
    :param number load: amount to borrow
    #FIXME: put in the correct information for feature
    :param ?? feature:
    :param float apr: annual interest rate of the loan
    :param int maturity: maturity for the loan
    :
    """
    loan = float(loan)

    payment = 0*feature + loan*(apr)*(1+apr)**(maturity)  \
        / ((1+apr)**(maturity)-1)
    return '{0:6,.0f}'.format(loan), '{0:6,.0f}'.format(payment)


# FIXME: add function level comment
def cost_breakdown(build_dadu, size):
    # CHANGED: Use PEP8 convention for variable names
    """
    Calculates various cost for ADU construction
    :param boolean build_dadu: if building a DADU
    :param float size: the square footage of potential adu
    """
    construction = float(np.array([build_dadu]).astype(int))*C.DADU_FIXED + \
        C.ADU_VAR*float(size)

    construction_min = construction*(1-C.MULTIPLIER)

    construction_max = construction*(1+C.MULTIPLIER)

    tax_min = construction_min*C.SALES_TAX

    tax_max = construction_max*C.SALES_TAX

    sewer = float(np.array([build_dadu]).astype(int))*C.DADU_SEWER +  \
        (1-float(np.array([build_dadu]).astype(int)))*C.AADU_SEWER

    permit = C.PERMIT_FIXED + float(size)*C.PERMIT_VAR

    design_min = float(construction_min)*C.DESIGN_PERCENTAGE
    design_max = float(construction_max)*C.DESIGN_PERCENTAGE

    total_min = construction_min + tax_min + sewer + design_min + permit
    total_max = construction_max + tax_max + sewer + design_max + permit

    property_tax = (total_min+total_max)/2*C.PROPERTY_TAX

    return '({0:6,.0f} -- {1:6,.0f})'.format(construction_min, construction_max), \
           '({0:6,.0f} -- {1:6,.0f})'.format(tax_min, tax_max), \
        '{0:6,.0f}'.format(sewer), '{0:6,.0f}'.format(permit), \
        '({0:6,.0f} -- {1:6,.0f})'.format(design_min, design_max), \
        '({0:6,.0f} -- {1:6,.0f})'.format(total_min, total_max), \
        '{0:6,.0f}'.format(property_tax)