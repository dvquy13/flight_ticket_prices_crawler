import scrapy
import scrapy_splash
import pandas as pd
import os

from ..utils import extract as extract_utils
from ..utils import file as file_utils


class TravelokaSpider(scrapy.Spider):
    name = 'traveloka'
    o_path = './output/result.csv'

    def start_requests(self):
        urls = [
            'https://www.traveloka.com/vi-vn/flight/fulltwosearch?ap=HAN.PQC&dt=12-05-2019.15-05-2019&ps=1.0.0&sc=ECONOMY'
            'https://www.traveloka.com/vi-vn/flight/fulltwosearch?ap=HAN.PQC&dt=12-05-2019.15-05-2019&ps=1.0.0&sc=ECONOMY#depart',
            'https://www.traveloka.com/vi-vn/flight/fulltwosearch?ap=HAN.PQC&dt=12-05-2019.15-05-2019&ps=1.0.0&sc=ECONOMY#return'
        ]

        for url in urls:
            if url.endswith('#depart'):
                yield scrapy_splash.SplashRequest(url, self.parse_depart,
                    args={
                        # optional; parameters passed to Splash HTTP API
                        'wait': 5,

                        # 'url' is prefilled from request url
                        # 'http_method' is set to 'POST' for POST requests
                        # 'body' is set to request body for POST requests
                    },
                    # endpoint='render.json', # optional; default is render.html
                    # splash_url='<url>',     # optional; overrides SPLASH_URL
                    # slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,  # optional
                )
            elif url.endswith('#return'):
                yield scrapy_splash.SplashRequest(url, self.parse_return,
                    args={
                        # optional; parameters passed to Splash HTTP API
                        'wait': 0.5,

                        # 'url' is prefilled from request url
                        # 'http_method' is set to 'POST' for POST requests
                        # 'body' is set to request body for POST requests
                    },
                    # endpoint='render.json', # optional; default is render.html
                    # splash_url='<url>',     # optional; overrides SPLASH_URL
                    # slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,  # optional
                )


    def parse_depart(self, response):
        res_df = (
            extract_utils.extract_flight_info(response)
            .assign(
                direction='Hanoi -> Phu Quoc',
                import_time=pd.Timestamp.now())
        )

        filter_df = pd.concat(
            [
                res_df
                    .loc[
                        lambda df:
                            df['price'] == df['price'].min()]
                    .assign(type='cheapest'),
                res_df
                    .loc[
                        lambda df:
                            (df['airline'] == 'Jetstar')
                            &
                            (df['depart_time'] == '09:45')]
                    .assign(type='family')
            ],
            axis=0
        )
        import pdb; pdb.set_trace()
        file_utils.save_or_append(filter_df, path=self.o_path)
        self.log(f"Saved depart output!")

    
    def parse_return(self, response):
        res_df = (
            extract_utils.extract_flight_info(response)
            .assign(
                direction='Phu Quoc -> Hanoi',
                import_time=pd.Timestamp.now())
        )

        filter_df = pd.concat(
            [
                res_df
                    .loc[
                        lambda df:
                            df['price'] == df['price'].min()]
                    .assign(type='cheapest'),
                res_df
                    .loc[
                        lambda df:
                            (df['airline'] == 'Jetstar')
                            &
                            (df['depart_time'] == '12:30')]
                    .assign(type='family')
            ],
            axis=0
        )

        file_utils.save_or_append(filter_df, path=self.o_path)
        self.log(f"Saved return output!")
