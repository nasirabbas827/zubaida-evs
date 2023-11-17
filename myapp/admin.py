# admin.py

from django.contrib import admin
from .models import Voter, Profile, Election, Candidate, Vote

class VoteAdmin(admin.ModelAdmin):
    list_display = ('election', 'candidate', 'voter_id', 'timestamp')
    readonly_fields = ('election', 'candidate', 'voter_id', 'timestamp', 'previous_hash', 'current_hash', 'data', 'nonce')

    def has_add_permission(self, request):
        # Disable the ability to add new Vote instances
        return False

    def has_change_permission(self, request, obj=None):
        # Disable the ability to change existing Vote instances
        return True  # Set this to False if you want to completely disable changing as well

admin.site.register(Voter)
admin.site.register(Profile)
admin.site.register(Election)
admin.site.register(Candidate)
admin.site.register(Vote, VoteAdmin)
