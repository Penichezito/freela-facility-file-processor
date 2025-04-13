from marshmallow import Schema, fields, validate, validates, ValidationError
from werkzeug.datastructures import FileStorage


class FileSchema(Schema):
    """Schema for File model."""
    id = fields.Integer(dump_only=True)
    original_filename = fields.String(required=True)
    stored_filename = fields.String(dump_only=True)
    file_path = fields.String(dump_only=True)
    file_type = fields.String(dump_only=True)
    file_size = fields.Integer(dump_only=True)
    content_type = fields.String(dump_only=True)
    metadata = fields.Dict(dump_only=True)
    
    external_id = fields.Integer(allow_none=True)
    project_id = fields.Integer(allow_none=True)
    uploader_id = fields.Integer(allow_none=True)
    
    tags = fields.List(fields.String(), dump_only=True)
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class FileUploadSchema(Schema):
    """Schema for file upload."""
    file = fields.Raw(required=True, type="file")
    metadata = fields.Dict(required=False)
    
    @validates("file")
    def validate_file(self, file):
        if not isinstance(file, FileStorage):
            raise ValidationError("Not a valid file")


class FileMetadataSchema(Schema):
    """Schema for file metadata updates."""
    metadata = fields.Dict(required=True)


class FileQuerySchema(Schema):
    """Schema for file queries."""
    project_id = fields.Integer(required=False)
    uploader_id = fields.Integer(required=False)
    file_type = fields.String(required=False)
    tags = fields.List(fields.String(), required=False)
    
    limit = fields.Integer(validate=validate.Range(min=1, max=100), missing=20)
    offset = fields.Integer(validate=validate.Range(min=0), missing=0)


file_schema = FileSchema()
files_schema = FileSchema(many=True)
file_upload_schema = FileUploadSchema()
file_metadata_schema = FileMetadataSchema()
file_query_schema = FileQuerySchema()