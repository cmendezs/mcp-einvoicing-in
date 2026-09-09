# mcp-einvoicing-in 🇮🇳

[English](README.md) | [हिन्दी](README.hi.md)

<!-- mcp-name: io.github.cmendezs/mcp-einvoicing-in -->

![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)
[![PyPI version](https://img.shields.io/pypi/v/mcp-einvoicing-in.svg)](https://pypi.org/project/mcp-einvoicing-in/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-einvoicing-in.svg)](https://pypi.org/project/mcp-einvoicing-in/) [![mcp-einvoicing-in MCP server](https://glama.ai/mcp/servers/cmendezs/mcp-einvoicing-in/badges/score.svg)](https://glama.ai/mcp/servers/cmendezs/mcp-einvoicing-in)

यह एक Python MCP सर्वर है जो भारत के **GST ई-इनवॉइसिंग** के लिए टूल्स प्रदान करता है, GSTN के
**FORM GST INV-01 schema v1.1** के अनुसार (CGST अधिनियम 2017 की धारा 31 + CGST नियम 48(4),
Notification No. 68/2019-Central Tax)। यह AI एजेंट्स (Claude, IDEs) को GST ई-इनवॉइस के JSON
पेलोड (INV, CRN, DBN दस्तावेज़ प्रकार) बनाने और उनकी संरचनात्मक जाँच करने, तथा IRP द्वारा लौटाए
गए signed QR स्ट्रिंग को प्रदर्शन-योग्य इमेज के रूप में रेंडर करने में सक्षम बनाता है।

**Phase A स्कोप।** यह पैकेज केवल ऑफ़लाइन पेलोड निर्माण, संरचनात्मक जाँच, और GSTIN कर-पहचानकर्ता
सत्यापन को कवर करता है। यह Invoice Registration Portal (IRP) को **सबमिट नहीं करता** — लाइव सबमिशन
(auth/token, generate-IRN, cancel-IRN) एक बाद का चरण है, जो NIC e-invoice API विनिर्देश (specification)
अभी इस प्रोजेक्ट को उपलब्ध न होने के कारण रुका हुआ है (नीचे "विनिर्देशों की उपलब्धता" देखें)। यह
पैकेज आज वास्तव में क्या लागू करता है, इसके लिए [Available tools](#available-tools) देखें।

---

## परिचय

यह पैकेज [**mcp-einvoicing-core**](https://github.com/cmendezs/mcp-einvoicing-core) पर बना है,
जो e-invoicing MCP सर्वरों के लिए साझा आधार लाइब्रेरी है। यह `InvoiceDocument` मॉडल आधार और
`TaxIdentifier.validate_in_gstin` GSTIN वैलिडेटर प्रदान करता है।

`mcp-einvoicing-core` एक निर्भरता के रूप में स्वचालित रूप से इंस्टॉल होता है, किसी अतिरिक्त कदम
की आवश्यकता नहीं है।

GST ई-इनवॉइसिंग एक **क्लियरेंस-मॉडल** प्रणाली है: कोई इनवॉइस तभी कानूनी रूप से वैध बनता है जब
IRP (Invoice Registration Portal, NIC द्वारा संचालित) आपूर्तिकर्ता के JSON पेलोड को सत्यापित करता
है और एक Invoice Reference Number (IRN), पावती संख्या/तारीख, और एक signed QR कोड लौटाता है
(CGST नियम 48(4)/(5))। यह पैकेज वह अनुरोध पेलोड बनाता और उसकी संरचनात्मक जाँच करता है जिसे एक
आपूर्तिकर्ता सबमिट करेगा; यह स्वयं IRP को सबमिट नहीं करता (ऊपर "Phase A स्कोप" देखें)।

## इंस्टॉलेशन

### PyPI के माध्यम से (अनुशंसित)

```bash
pip install mcp-einvoicing-in
```

या पूर्व इंस्टॉलेशन के बिना `uvx` का उपयोग करके:

```bash
uvx mcp-einvoicing-in
```

### स्रोत से

```bash
git clone https://github.com/cmendezs/mcp-einvoicing-in.git
cd mcp-einvoicing-in
pip install -e ".[dev]"
```

## कॉन्फ़िगरेशन

इस पैकेज के वर्तमान (Phase A) स्कोप के लिए किसी environment variable की आवश्यकता नहीं है — यह
कोई नेटवर्क कॉल नहीं करता। लाइव IRP सबमिशन, एक बार लागू होने पर, IRP/GSP क्रेडेंशियल्स की
आवश्यकता होगी; उस समय यह सेक्शन अपडेट किया जाएगा।

## Claude Desktop एकीकरण

अपनी Claude Desktop कॉन्फ़िगरेशन फ़ाइल (`claude_desktop_config.json`) में जोड़ें:

```json
{
  "mcpServers": {
    "einvoicing-in": {
      "command": "uvx",
      "args": ["mcp-einvoicing-in"]
    }
  }
}
```

## Cursor एकीकरण

वही `mcpServers` ब्लॉक इनमें से किसी एक में जोड़ें:

- वैश्विक (Global): `~/.cursor/mcp.json`
- प्रोजेक्ट-विशिष्ट: आपके प्रोजेक्ट रूट में `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "einvoicing-in": {
      "command": "uvx",
      "args": ["mcp-einvoicing-in"]
    }
  }
}
```

सहेजने के बाद Cursor को रीलोड करें (या कमांड पैलेट से "Reload Window" चलाएँ)।

## Kiro एकीकरण

इनमें से किसी एक में जोड़ें:

- वैश्विक (Global): `~/.kiro/settings/mcp.json`
- Workspace: `.kiro/settings/mcp.json`

```json
{
  "mcpServers": {
    "einvoicing-in": {
      "command": "uvx",
      "args": ["mcp-einvoicing-in"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Kiro सहेजने पर MCP कॉन्फ़िगरेशन को स्वचालित रूप से रीलोड करता है। यदि इस पैकेज के किसी भविष्य के
संस्करण को क्रेडेंशियल्स की आवश्यकता होती है, तो इस फ़ाइल में plaintext secrets के बजाय
`"VAR_NAME": "${VAR_NAME}"` शेल-इंटरपोलेशन सिंटैक्स को प्राथमिकता दें।

## Available tools

### Scope

- `in__get_supported_scope` — इस पैकेज द्वारा वर्तमान में समर्थित दस्तावेज़ प्रकार, आपूर्ति
  प्रकार, और स्पष्ट रूप से स्कोप से बाहर की वस्तुओं को लौटाता है।

### Build and validate

- `in__build_invoice` — संरचित इनपुट को `INInvoice` के विरुद्ध सत्यापित करता है और एक GST
  ई-इनवॉइस JSON पेलोड (INV/CRN/DBN) बनाता है। यह कभी भी `IRN` उत्सर्जित नहीं करता — वह फ़ील्ड
  IRP-जनित होती है, आपूर्तिकर्ता द्वारा कभी नहीं भरी जाती।
- `in__validate_invoice` — ऑफ़लाइन संरचनात्मक/व्यावसायिक-नियम सत्यापन: अनिवार्य फ़ील्ड, enum
  सदस्यता, CGST+SGST-बनाम-IGST युग्मन (आइटम और दस्तावेज़-कुल स्तर पर), और GSTIN/राज्य-कोड
  स्थिरता। यहाँ कोई XSD/Schematron पास नहीं है — FORM GST INV-01 JSON है, XML नहीं।

### QR

- `in__render_irp_qr_png` — IRP द्वारा लौटाई गई signed QR स्ट्रिंग को प्रदर्शन-योग्य PNG के रूप
  में रेंडर करता है। यह QR की सामग्री को डिकोड या व्याख्यायित नहीं करता — जो NIC e-invoice API
  विनिर्देश उस सामग्री का दस्तावेज़ीकरण करता, वह अभी इस प्रोजेक्ट को उपलब्ध नहीं है (नीचे
  "विनिर्देशों की उपलब्धता" देखें)।

## विनिर्देशों की उपलब्धता

भारत के बाहर से वर्तमान, सटीक NIC/GSTN तकनीकी विनिर्देश प्राप्त करना अविश्वसनीय है: GSTN कड़े
भौगोलिक फ़ायरवॉल लागू करता है जो अक्सर गैर-भारतीय IP पतों को अवरुद्ध या दर-सीमित करते हैं। यह
पैकेज पूरी तरह से मेंटेनर द्वारा सीधे उपलब्ध कराए गए विनिर्देश दस्तावेज़ों (FORM GST INV-01
schema v1.1; CGST Notifications 68/2019-CT तथा 72/2020-CT; और Notification No. 10/2023-CT, जो
वर्तमान AATO अनिवार्यता-सीमा की पुष्टि करता है) से बनाया गया है — किसी भी दस्तावेज़ को किसी
स्वचालित एजेंट द्वारा इंटरनेट से नहीं लाया गया। इसके प्रत्यक्ष परिणामस्वरूप:

- **इस प्रोजेक्ट को अभी उपलब्ध नहीं:** पूरी सूची [`specs/README.md`](specs/README.md) की
  "Pending specs" तालिका में देखें।
- NIC e-invoice API विनिर्देश के बिना लाइव IRP सबमिशन टूल्स को ज़िम्मेदारी से नहीं बनाया जा सकता —
  "Phase A स्कोप" देखें।

**यदि आप भारत में स्थित हैं और वहाँ सूचीबद्ध किसी भी दस्तावेज़ को उपलब्ध करा सकते हैं**, तो कृपया
[Spec Update issue template](https://github.com/cmendezs/mcp-einvoicing-in/issues/new?template=spec-update.yml)
का उपयोग करके एक issue खोलें। यह टेम्पलेट दस्तावेज़ का नाम, आधिकारिक स्रोत URL, संस्करण, और
प्राप्ति तिथि दर्ज करता है; उसके बाद एक follow-up pull request `specs/` के अंतर्गत फ़ाइल के साथ-साथ
एक sources-table प्रविष्टि और एक provenance/redistribution पुष्टिकरण जोड़ता है। पूरी दो-चरणीय
प्रक्रिया के लिए [CONTRIBUTING.md](CONTRIBUTING.md) देखें।

## Architecture

`INInvoice`, `InvoiceDocument` (`mcp_einvoicing_core.models`) को subclass करता है — FORM GST
INV-01 का कोई EN 16931/UBL/CII वंश नहीं है (यह एक फ़्लैट JSON क्लियरेंस-मॉडल schema है), इसलिए
यह पैकेज उसी `InvoiceDocument` पथ का अनुसरण करता है जिसका उपयोग `mcp-cfdi-mx` (CFDI) और
`mcp-nfe-br` (NF-e) करते हैं। `INInvoiceLine`, `InvoiceLineItem` को subclass करके schema के
GST/HSN/cess फ़ील्ड जोड़ता है, जिनका आधार लाइन-आइटम मॉडल में कोई समकक्ष नहीं है। GSTIN फ़ील्ड
`TaxIdentifier.validate_in_gstin` के माध्यम से सत्यापित होते हैं, जिसे `INInvoice` के अपने मॉडल
validators से कॉल किया जाता है — यह पैकेज कभी भी पहचानकर्ता-सत्यापन तर्क को स्थानीय रूप से फिर से
लागू नहीं करता। यहाँ कोई Schematron/XSD validator परत नहीं है (`validators/structural.py` इसके
बजाय सादे-Python व्यावसायिक-नियम जाँच लागू करता है), क्योंकि वायर फॉर्मेट JSON है, XML नहीं।

## विक्रेता तटस्थता

यह सर्वर मानक को स्वयं लागू करता है: यह दस्तावेज़ को स्थानीय रूप से बनाता और सत्यापित करता है।
यह किसी वाणिज्यिक इनवॉइसिंग प्लेटफ़ॉर्म का क्लाइंट नहीं है, और आपकी क्रेडेंशियल्स कभी भी आपके अपने
इन्फ्रास्ट्रक्चर से बाहर नहीं जातीं।

IRP तक पहुँचने के लिए एक GSP (GST Suvidha Provider) की आवश्यकता होगी; यह पैकेज पेलोड को स्थानीय
रूप से बनाता और संरचनात्मक रूप से सत्यापित करता है, और वास्तविक IRP सबमिशन अभी तक लागू नहीं किया
गया है, जो NIC API स्पेसिफिकेशन की प्रतीक्षा में है (ऊपर "Spec availability" देखें)।

## Contributing

डेवलपमेंट सेटअप, PR चेकलिस्ट, और कमिट शैली के लिए [CONTRIBUTING.md](CONTRIBUTING.md) देखें।

## Other e-invoicing MCP servers

| Country | Server |
|---------|--------|
| 🌍 Global | [mcp-einvoicing-core](https://github.com/cmendezs/mcp-einvoicing-core) |
| 🇧🇪 Belgium | [mcp-einvoicing-be](https://github.com/cmendezs/mcp-einvoicing-be) |
| 🇧🇷 Brazil | [mcp-nfe-br](https://github.com/cmendezs/mcp-nfe-br) |
| 🇫🇷 France | [mcp-facture-electronique-fr](https://github.com/cmendezs/mcp-facture-electronique-fr) |
| 🇩🇪 Germany | [mcp-einvoicing-de](https://github.com/cmendezs/mcp-einvoicing-de) |
| 🇮🇳 India | [mcp-einvoicing-in](https://github.com/cmendezs/mcp-einvoicing-in) |
| 🇮🇹 Italy | [mcp-fattura-elettronica-it](https://github.com/cmendezs/mcp-fattura-elettronica-it) |
| 🇲🇽 Mexico | [mcp-cfdi-mx](https://github.com/cmendezs/mcp-cfdi-mx) |
| 🇵🇱 Poland | [mcp-ksef-pl](https://github.com/cmendezs/mcp-ksef-pl) |
| 🇸🇬 Singapore | [mcp-invoicenow-sg](https://github.com/cmendezs/mcp-invoicenow-sg) |
| 🇪🇸 Spain | [mcp-facturacion-electronica-es](https://github.com/cmendezs/mcp-facturacion-electronica-es) |
| 🇦🇪 United Arab Emirates | [mcp-einvoicing-ae](https://github.com/cmendezs/mcp-einvoicing-ae) |

## License

This project is licensed under the **Apache 2.0** license — see [LICENSE](LICENSE) for details.
For the full version history, see [CHANGELOG.md](CHANGELOG.md).
