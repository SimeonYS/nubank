import json
import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import NnubankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'
base = 'https://blog.nubank.com.br/wp-admin/admin-ajax.php?action=get_more_posts&offset={}&category=1&type=post&tag=&author=&id=650798894&width=1920&__amp_source_origin=https%3A%2F%2Fblog.nubank.com.br'

class NnubankSpider(scrapy.Spider):
	name = 'nubank'
	offset = 0
	start_urls = [base.format(offset)]

	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data['items'])):
			title = data['items'][index]['title']
			date = data['items'][index]['date']
			link = data['items'][index]['link']
			yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date, title=title))

		if data['has_more_pages']:
			self.offset += 4
			yield response.follow(base.format(self.offset), self.parse)

	def parse_post(self, response, date, title):
		content = response.xpath('//main[@class="article-main main-side inner-container"]//text()[not (ancestor::noscript)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=NnubankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
