from django.contrib.auth.models import User
from django.db import models

class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    voter_id = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.user.username

from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, default="John Doe")  # Default full name
    email = models.EmailField(default="example@example.com")  # Default email address

    def __str__(self):
        return self.user.username


from django.db import models

from django.db import models

class Election(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('ongoing', 'Ongoing'), ('completed', 'Completed')], default='ongoing')
    
    def __str__(self):
        return self.title

class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    party = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to='candidate_images/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class Vote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    voter_id = models.IntegerField()  # Replace this with the appropriate user identifier in your system
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Blockchain-related fields
    previous_hash = models.CharField(max_length=64, blank=True, null=True)
    current_hash = models.CharField(max_length=64, blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    nonce = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Vote for {self.candidate.name} in {self.election.title} by {self.voter_id}"