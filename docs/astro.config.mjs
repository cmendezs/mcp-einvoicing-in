import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import starlightLlmsTxt from "starlight-llms-txt";

export default defineConfig({
  site: "https://cmendezs.github.io",
  base: "/mcp-einvoicing-in/",
  integrations: [
    starlight({
      title: "mcp-einvoicing-in",
      description: "MCP server for India GST e-invoicing (FORM GST INV-01 schema v1.1 / IRP-IRN)",
      customCss: ["./src/styles/docs-theme.css"],
      social: [
        { icon: "github", label: "GitHub", href: "https://github.com/cmendezs/mcp-einvoicing-in" },
      ],
      locales: {
        root: { label: "English", lang: "en" },
        hi: { label: "हिन्दी", lang: "hi" },
      },
      sidebar: [
        { label: "Overview", link: "/" },
        { label: "Tools", link: "/tools/" },
        { label: "Changelog", link: "/changelog/" },
        { label: "Contributing", link: "/contributing/" },
        { label: "Security", link: "/security/" },
        { label: "Code of Conduct", link: "/code-of-conduct/" },
      ],
      plugins: [
        starlightLlmsTxt({
          projectName: "mcp-einvoicing-in",
          description: "MCP server for India GST e-invoicing (FORM GST INV-01 schema v1.1 / IRP-IRN)",
          customSets: [
            {
              label: "Key links",
              description: "PyPI and MCP registry entries",
              links: ["https://pypi.org/project/mcp-einvoicing-in/", "https://registry.modelcontextprotocol.io/v0/servers?search=io.github.cmendezs/mcp-einvoicing-in"],
            },
          ],
        }),
      ],
    }),
  ],
});
