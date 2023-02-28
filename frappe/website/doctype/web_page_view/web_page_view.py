# Copyright (c) 2020, Frappe Technologies and contributors
# License: MIT. See LICENSE

from urllib.parse import urlparse

import frappe
import frappe.utils
from frappe.model.document import Document


class WebPageView(Document):
	pass


@frappe.whitelist(allow_guest=True)
def make_view_log(
	referrer=None,
	browser=None,
	version=None,
	user_tz=None,
	utm_source=None,
	utm_medium=None,
	utm_campaign=None,
	utm_term=None,
	utm_content=None,
	visitor_id=None,
):
	if not is_tracking_enabled():
		return

	# real path
	path = frappe.request.headers.get("Referer")

	if not frappe.utils.is_site_link(path):
		return

	path = urlparse(path).path

	request_dict = frappe.request.__dict__
	user_agent = request_dict.get("environ", {}).get("HTTP_USER_AGENT")

	if referrer:
		referrer = referrer.split("?", 1)[0]

	if path != "/" and path.startswith("/"):
		path = path[1:]

	is_unique = visitor_id and not bool(frappe.db.exists("Web Page View", {"visitor_id": visitor_id}))

	view = frappe.new_doc("Web Page View")
	view.path = path
	view.referrer = referrer
	view.browser = browser
	view.browser_version = version
	view.time_zone = user_tz
	view.user_agent = user_agent
	view.is_unique = is_unique
	view.utm_source = utm_source
	view.utm_medium = utm_medium
	view.utm_campaign = utm_campaign
	view.utm_term = utm_term
	view.utm_content = utm_content
	view.visitor_id = visitor_id

	try:
		if frappe.flags.read_only:
			view.deferred_insert()
		else:
			view.insert(ignore_permissions=True)
	except Exception:
		if frappe.message_log:
			frappe.message_log.pop()


@frappe.whitelist()
def get_page_view_count(path):
	return frappe.db.count("Web Page View", filters={"path": path})


def is_tracking_enabled():
	return frappe.db.get_single_value("Website Settings", "enable_view_tracking")
