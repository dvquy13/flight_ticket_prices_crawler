import requests
import datetime
import pandas as pd
import config
import argparse

import utils

def post_via_webhook(message, attachments, channel):
    req = {
        "channel": channel['channel'],
        "username": channel['username'],
        "text": message,
        "icon_emoji": ":airplane:",
        "mrkdwn": True,
        "attachments": attachments
    }

    resp = requests.post(channel['incoming_webhook_url'], json=req)
    print("Request: ", req)
    print("Response: ", resp.content)


class FlightTicketPricesCrawlReport:
    def __init__(self):
        pass


    @staticmethod
    def report_first_time(df: pd.DataFrame, direction: str, crawl_type: str):
        import_time = df['import_time'].values[0]
        cheapest_price = df['price'].min()
        res = f"[{utils.get_current_timestr(import_time)}] Current {crawl_type} price for {direction} flight is `{cheapest_price:,.0f} VND`"
        return res


    @staticmethod
    def report_difference(df: pd.DataFrame, direction: str, crawl_type: str):
        df = df.sort_values(['import_time', 'price'], ascending=[False, True])
        filtered_df = df.groupby(['import_time']).head(1)
        import_time = df['import_time'].values[0]
        current_cheapest_price = filtered_df.iloc[0]['price']
        previous_cheapest_price = filtered_df.iloc[1]['price']
        mess = None
        if current_cheapest_price != previous_cheapest_price:
            abs_diff = previous_cheapest_price - current_cheapest_price
            perc_diff = float(abs_diff) / previous_cheapest_price
            if abs(perc_diff) >= 0.05:
                mess = f"[{utils.get_current_timestr(import_time)}] New {crawl_type} price for {direction} ticket: *{current_cheapest_price:,.0f} VND* ({utils.get_arrow(current_cheapest_price, previous_cheapest_price)} {abs(abs_diff):,.0f} VND - _{abs(perc_diff):,.1%}_) compared to previous cheapest {previous_cheapest_price:,.0f} VND"
        return mess


    @staticmethod
    def report_by_type(df: pd.DataFrame, direction: str, crawl_type: str):
        type_cheapest = df.loc[lambda df: df['crawl_type'] == crawl_type]
        if type_cheapest['import_time'].nunique() == 1:
            type_cheapest_mess = FlightTicketPricesCrawlReport.report_first_time(type_cheapest, direction=direction, crawl_type=crawl_type)
        else:
            type_cheapest_mess = FlightTicketPricesCrawlReport.report_difference(type_cheapest, direction=direction, crawl_type=crawl_type)
        return type_cheapest_mess


    def report(self, output_file ="./output/result.csv", verbose=1):
        output = pd.read_csv(output_file, parse_dates=['import_time'])
        depart_output = output.loc[lambda df: df['direction'] == 'depart']
        return_output = output.loc[lambda df: df['direction'] == 'return']
        
        # Report cheapest
        depart_cheapest_mess = FlightTicketPricesCrawlReport.report_by_type(depart_output, direction='depart', crawl_type = 'cheapest')
        return_cheapest_mess = FlightTicketPricesCrawlReport.report_by_type(return_output, direction='return', crawl_type = 'cheapest')
        depart_family_mess = FlightTicketPricesCrawlReport.report_by_type(depart_output, direction='depart', crawl_type = 'family')
        return_family_mess = FlightTicketPricesCrawlReport.report_by_type(return_output, direction='return', crawl_type = 'family')
        mess = [depart_cheapest_mess, return_cheapest_mess, depart_family_mess, return_family_mess]
        mess = [x for x in mess if x is not None]
        
        post_via_webhook('\n'.join(mess), attachments=None, channel=config.SLACK_CHANNELS[0])


def main(args):
    reporter = FlightTicketPricesCrawlReport()
    reporter.report(verbose=args.verbose)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--verbose", type=int, default=1)
    args = parser.parse_args()

    main(args)
