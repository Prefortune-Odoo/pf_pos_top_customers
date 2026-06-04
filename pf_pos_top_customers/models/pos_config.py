from odoo import models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    def name_get(self):
        if self.env.context.get('show_company_in_pos_config'):
            result = []
            for config in self:
                name = config.name
                if config.company_id:
                    name = f"{name} ({config.company_id.name})"
                result.append((config.id, name))
            return result
        if hasattr(super(), 'name_get'):
            return super().name_get()
        return [(r.id, r.display_name) for r in self]

    def _compute_display_name(self):
        if hasattr(super(), '_compute_display_name'):
            super()._compute_display_name()
        for config in self:
            if self.env.context.get('show_company_in_pos_config') and config.company_id:
                config.display_name = f"{config.name} ({config.company_id.name})"

