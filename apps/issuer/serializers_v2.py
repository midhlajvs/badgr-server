import uuid

import os
from collections import OrderedDict

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator, EmailValidator, RegexValidator
from rest_framework import serializers

from badgeuser.models import BadgeUser
from entity.serializers import DetailSerializerV2, EntityRelatedFieldV2, BaseSerializerV2
from issuer.models import Issuer, IssuerStaff, BadgeClass, BadgeInstance
from mainsite.drf_fields import ValidImageField
from mainsite.serializers import StripTagsCharField, MarkdownCharField, HumanReadableBooleanField, \
    OriginalJsonSerializerMixin
from mainsite.validators import ChoicesValidator, TelephoneValidator


class IssuerStaffSerializerV2(DetailSerializerV2):
    user = EntityRelatedFieldV2(source='cached_user', queryset=BadgeUser.cached)
    role = serializers.CharField(validators=[ChoicesValidator(dict(IssuerStaff.ROLE_CHOICES).keys())])

    class Meta(DetailSerializerV2.Meta):
        apispec_definition = ('IssuerStaff', {
            'properties': {
                'role': {
                    'type': "string",
                    'enum': ["staff", "editor", "owner"]

                }
            }
        })


class IssuerSerializerV2(DetailSerializerV2, OriginalJsonSerializerMixin):
    openBadgeId = serializers.URLField(source='jsonld_id', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    createdBy = EntityRelatedFieldV2(source='cached_creator', read_only=True)
    name = StripTagsCharField(max_length=1024)
    image = ValidImageField(required=False)
    email = serializers.EmailField(max_length=255, required=True)
    description = StripTagsCharField(max_length=1024, required=True)
    url = serializers.URLField(max_length=1024, required=True)
    staff = IssuerStaffSerializerV2(many=True, source='staff_items', required=False)

    class Meta(DetailSerializerV2.Meta):
        model = Issuer
        apispec_definition = ('Issuer', {
            'properties': OrderedDict([
                ('entityId', {
                    'type': "string",
                    'format': "string",
                    'description': "Unique identifier for this Issuer",
                }),
                ('entityType', {
                    'type': "string",
                    'format': "string",
                    'description': "\"Issuer\"",
                }),
                ('openBadgeId', {
                    'type': "string",
                    'format': "url",
                    'description': "URL of the OpenBadge compliant json",
                }),
                ('createdAt', {
                    'type': 'string',
                    'format': 'ISO8601 timestamp',
                    'description': "Timestamp when the Issuer was created",
                }),
                ('createdBy', {
                    'type': 'string',
                    'format': 'entityId',
                    'description': "BadgeUser who created this Issuer",
                }),

                ('name', {
                    'type': "string",
                    'format': "string",
                    'description': "Name of the Issuer",
                }),
                ('image', {
                    'type': "string",
                    'format': "data:image/png;base64",
                    'description': "Base64 encoded string of an image that represents the Issuer",
                }),
                ('email', {
                    'type': "string",
                    'format': "email",
                    'description': "Contact email for the Issuer",
                }),
                ('url', {
                    'type': "string",
                    'format': "url",
                    'description': "Homepage or website associated with the Issuer",
                }),
                ('description', {
                    'type': "string",
                    'format': "text",
                    'description': "Short description of the Issuer",
                }),

            ])
        })

    def validate_image(self, image):
        if image is not None:
            img_name, img_ext = os.path.splitext(image.name)
            image.name = 'issuer_logo_' + str(uuid.uuid4()) + img_ext
        return image

    def create(self, validated_data):
        staff = validated_data.pop('staff_items')
        new_issuer = super(IssuerSerializerV2, self).create(validated_data)

        # update staff after issuer is created
        new_issuer.staff_items = staff

        return new_issuer


class AlignmentItemSerializerV2(BaseSerializerV2, OriginalJsonSerializerMixin):
    targetName = StripTagsCharField(source='target_name')
    targetUrl = serializers.URLField(source='target_url')
    targetDescription = StripTagsCharField(source='target_description', required=False)
    targetFramework = StripTagsCharField(source='target_framework', required=False)
    targetCode = StripTagsCharField(source='target_code', required=False)

    class Meta:
        apispec_definition = ('BadgeClassAlignment', {
            'properties': {
            }
        })


class BadgeClassSerializerV2(DetailSerializerV2, OriginalJsonSerializerMixin):
    openBadgeId = serializers.URLField(source='jsonld_id', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    createdBy = EntityRelatedFieldV2(source='cached_creator', read_only=True)
    issuer = EntityRelatedFieldV2(source='cached_issuer', required=False, queryset=Issuer.cached)

    name = StripTagsCharField(max_length=1024)
    image = ValidImageField(required=False)
    description = StripTagsCharField(max_length=1024, required=True)

    criteriaUrl = StripTagsCharField(source='criteria_url', required=False, allow_null=True, validators=[URLValidator()])
    criteriaNarrative = MarkdownCharField(source='criteria_text', required=False, allow_null=True)

    alignments = AlignmentItemSerializerV2(source='cached_alignments', many=True, required=False)
    tags = serializers.ListField(child=StripTagsCharField(max_length=1024), source='tag_items', required=False)

    class Meta(DetailSerializerV2.Meta):
        model = BadgeClass
        apispec_definition = ('BadgeClass', {
            'properties': OrderedDict([
                ('entityId', {
                    'type': "string",
                    'format': "string",
                    'description': "Unique identifier for this BadgeClass",
                }),
                ('entityType', {
                    'type': "string",
                    'format': "string",
                    'description': "\"BadgeClass\"",
                }),
                ('openBadgeId', {
                    'type': "string",
                    'format': "url",
                    'description': "URL of the OpenBadge compliant json",
                }),
                ('createdAt', {
                    'type': 'string',
                    'format': 'ISO8601 timestamp',
                    'description': "Timestamp when the BadgeClass was created",
                }),
                ('createdBy', {
                    'type': 'string',
                    'format': 'entityId',
                    'description': "BadgeUser who created this BadgeClass",
                }),

                ('issuer', {
                    'type': 'string',
                    'format': 'entityId',
                    'description': "entityId of the Issuer who owns the BadgeClass",
                }),

                ('name', {
                    'type': "string",
                    'format': "string",
                    'description': "Name of the BadgeClass",
                }),
                ('description', {
                    'type': "string",
                    'format': "string",
                    'description': "Short description of the BadgeClass",
                }),
                ('image', {
                    'type': "string",
                    'format': "data:image/png;base64",
                    'description': "Base64 encoded string of an image that represents the BadgeClass.",
                }),
                ('criteriaUrl', {
                    'type': "string",
                    'format': "url",
                    'description': "External URL that describes in a human-readable format the criteria for the BadgeClass"
                }),
                ('criteriaNarrative', {
                    'type': "string",
                    'format': "markdown",
                    'description': "Markdown formatted description of the criteria"
                }),
                ('tags', {
                    'type': "array",
                    'items': {
                        'type': "string",
                        'format': "string"
                    },
                    'description': "List of tags that describe the BadgeClass"
                }),
                ('alignments', {
                    'type': "array",
                    'items': {
                        '$ref': '#/definitions/BadgeClassAlignment'
                    },
                    'description': "List of objects describing objectives or educational standards"
                }),
            ])
        })


    def update(self, instance, validated_data):
        if 'cached_issuer' in validated_data:
            validated_data.pop('cached_issuer')  # issuer is not updatable
        return super(BadgeClassSerializerV2, self).update(instance, validated_data)

    def create(self, validated_data):
        if 'cached_issuer' in validated_data:
            # included issuer in request
            validated_data['issuer'] = validated_data.pop('cached_issuer')
        elif 'issuer' in self.context:
            # issuer was passed in context
            validated_data['issuer'] = self.context.get('issuer')
        else:
            # issuer is required on create
            raise serializers.ValidationError({"issuer": "This field is required"})

        return super(BadgeClassSerializerV2, self).create(validated_data)




class BadgeRecipientSerializerV2(BaseSerializerV2):
    identity = serializers.CharField(source='recipient_identifier')
    type = serializers.ChoiceField(
        choices=BadgeInstance.RECIPIENT_TYPE_CHOICES,
        default=BadgeInstance.RECIPIENT_TYPE_EMAIL,
        required=False,
        source='recipient_type'
    )

    VALIDATORS = {
        BadgeInstance.RECIPIENT_TYPE_EMAIL: EmailValidator(),
        BadgeInstance.RECIPIENT_TYPE_URL: URLValidator(),
        BadgeInstance.RECIPIENT_TYPE_ID: URLValidator(),
        BadgeInstance.RECIPIENT_TYPE_TELEPHONE: TelephoneValidator(),
    }

    def validate(self, attrs):
        recipient_type = attrs.get('recipient_type')
        recipient_identifier = attrs.get('recipient_identifier')
        if recipient_type in self.VALIDATORS:
            try:
                self.VALIDATORS[recipient_type](recipient_identifier)
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.message)
        return attrs


class EvidenceItemSerializerV2(BaseSerializerV2, OriginalJsonSerializerMixin):
    url = serializers.URLField(source='evidence_url', max_length=1024, required=False)
    narrative = MarkdownCharField(required=False)

    def validate(self, attrs):
        if not (attrs.get('evidence_url', None) or attrs.get('narrative', None)):
            raise serializers.ValidationError("Either url or narrative is required")

        return attrs


class BadgeInstanceSerializerV2(DetailSerializerV2, OriginalJsonSerializerMixin):
    openBadgeId = serializers.URLField(source='jsonld_id', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    createdBy = EntityRelatedFieldV2(source='cached_creator', read_only=True)
    badgeclass = EntityRelatedFieldV2(source='cached_badgeclass', required=False, queryset=BadgeClass.cached)

    image = serializers.FileField(read_only=True)
    recipient = BadgeRecipientSerializerV2(source='*')

    issuedOn = serializers.DateTimeField(source='issued_on', required=False)
    narrative = MarkdownCharField(required=False)
    evidence = EvidenceItemSerializerV2(many=True, required=False)

    revoked = HumanReadableBooleanField(read_only=True)
    revocationReason = serializers.CharField(source='revocation_reason', read_only=True)
    
    class Meta(DetailSerializerV2.Meta):
        model = BadgeInstance
        
    def update(self, instance, validated_data):
        # BadgeInstances are not updatable
        return instance
    
    def create(self, validated_data):
        if 'cached_badgeclass' in validated_data:
            # included badgeclass in request
            validated_data['badgeclass'] = validated_data.pop('cached_badgeclass')
        elif 'badgeclass' in self.context:
            # badgeclass was passed in context
            validated_data['badgeclass'] = self.context.get('badgeclass')
        else:
            # badgeclass is required on create
            raise serializers.ValidationError({"badgeclass": "This field is required"})


        validated_data['issuer'] = validated_data['badgeclass'].issuer


        return super(BadgeInstanceSerializerV2, self).create(validated_data)

