'''
File: aggregateUncertainty.py
Description: Estimate uncertainty in a reduce operation given a list of alists to be reduced.


'''
import math
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank.util import utils


def estimate_uncertainty(nodes: list, all_numeric: bool, operation: str, child_count: float) -> float:
    combined_confidence = 0.0
    try:
        variance_values = []
        sum_variance = 0.0
        sum_mean = 0.0
        n = len(nodes)
        # todo: for now assume the real-valued objects are being estimated
        for r in nodes:
            node_variance = 0.0
            objValue = r.instantiation_value(tt.OBJECT)
            if utils.is_numeric(objValue):
                numeric_value = utils.get_number(objValue, 0)
                node_variance = math.pow(r.get(tt.COV) * numeric_value, 2)
                sum_mean += numeric_value
            else:
                # todo: work on this later; may not work as expected for non-real-valued objects
                node_variance = math.pow(r.get(tt.COV), 2)
                sum_mean += 1.0
            variance_values.append(node_variance)
            sum_variance += node_variance

        missRatio = 1 - (len(nodes)/child_count)
        if operation.lower() in ["value", "mean", "avg", "regress", "product"]:
            combined_confidence = math.sqrt(sum_variance/n)/(sum_mean/n)
        else:
            combined_confidence = math.sqrt(sum_variance)/(sum_mean/n)

        if not utils.is_numeric(combined_confidence):
            combined_confidence = 0.0
        combined_confidence = combined_confidence + \
            (combined_confidence * missRatio)

    except Exception as e:
        print("Uncertainty aggregate error: " + str(e))

    return combined_confidence
