from marshmallow import Schema, fields, validate, validates, ValidationError


class TagSchema(Schema):
    """Schema for Tag model."""
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(validate=validate.Length(max=255), allow_none=True)
    auto_generated = fields.Boolean(default=False)
    usage_count = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates("name")
    def validate_name(self, name):
        if not name or not name.strip():
            raise ValidationError("Tag name cannot be empty")


class TagCreateSchema(Schema):
    """Schema for creating a new tag."""
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(validate=validate.Length(max=255), allow_none=True)
    auto_generated = fields.Boolean(default=False)


class TagUpdateSchema(Schema):
    """Schema for updating an existing tag."""
    name = fields.String(validate=validate.Length(min=1, max=100))
    description = fields.String(validate=validate.Length(max=255), allow_none=True)
    auto_generated = fields.Boolean()


class TagQuerySchema(Schema):
    """Schema for tag queries."""
    search = fields.String(required=False)
    auto_generated = fields.Boolean(required=False, allow_none=True)
    
    limit = fields.Integer(validate=validate.Range(min=1, max=100), missing=20)
    offset = fields.Integer(validate=validate.Range(min=0), missing=0)


class FilesTagsSchema(Schema):
    """Schema for adding tags to a file."""
    tags = fields.List(fields.String(
        validate=validate.Length(min=1, max=100)), 
        required=True, 
        validate=validate.Length(min=1)
    )


tag_schema = TagSchema()
tags_schema = TagSchema(many=True)
tag_create_schema = TagCreateSchema()
tag_update_schema = TagUpdateSchema()
tag_query_schema = TagQuerySchema()
files_tags_schema = FilesTagsSchema()