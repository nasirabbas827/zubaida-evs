from django.contrib.auth import login, authenticate , logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page or wherever you need
                return redirect('dashboard')  # Replace 'success_page' with your desired URL
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Election, Candidate

@login_required
def dashboard(request):
    # Fetch the list of elections
    elections = Election.objects.all()
    
    # Fetch the list of candidates
    candidates = Candidate.objects.all()
    
    context = {
        'elections': elections,
        'candidates': candidates,
    }
    
    return render(request, 'dashboard.html', context)

# views.py

from django.shortcuts import render, get_object_or_404
from .models import Election, Candidate

def view_candidates(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    candidates = Candidate.objects.filter(election=election)

    context = {
        'election': election,
        'candidates': candidates,
    }

    return render(request, 'view_candidates.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm
from .models import Profile

@login_required
def update_profile(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        # Create a profile if it doesn't exist
        profile = Profile(user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            # Redirect to the profile update success page or dashboard
            return redirect('dashboard')  # Replace 'dashboard' with your dashboard URL name
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'update_profile.html', {'form': form})
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # To keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')  # Replace 'dashboard' with your dashboard URL name
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})

from django.contrib.auth import logout
from django.shortcuts import redirect

def voter_logout(request):
    logout(request)
    return redirect('user_login')  # You can specify the URL to redirect to after logout


# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Election, Candidate, Vote
from .blockchain import Blockchain

@login_required
def cast_vote(request, election_id, candidate_id):
    election = get_object_or_404(Election, pk=election_id)
    candidate = get_object_or_404(Candidate, pk=candidate_id)

    # Check if the election is ongoing
    if election.status != 'ongoing':
        return HttpResponse('Voting is not allowed for this election.')

    # Check if the user has already voted
    user_id = request.user.id
    if Vote.objects.filter(election=election, voter_id=user_id).exists():
        return HttpResponse('You have already voted in this election.')

    # Load the existing blockchain
    blockchain = Blockchain()

    # Record the vote in the database
    vote = Vote.objects.create(
        election=election,
        candidate=candidate,
        voter_id=user_id,
        previous_hash="",
        current_hash="",
        data="",
        nonce=0
    )

    # Add the vote information to the existing blockchain
    vote_data = f"{vote.election.id}-{vote.candidate.id}-{vote.voter_id}-{vote.timestamp}"
    previous_block = blockchain.chain[-1] if blockchain.chain else None
    vote.previous_hash = previous_block['current_hash'] if previous_block else ""
    vote.current_hash = blockchain.hash_block(vote.previous_hash, vote_data, vote.nonce)
    vote.data = vote_data
    vote.nonce = blockchain.proof_of_work(vote.previous_hash, vote_data, vote.timestamp)

    blockchain.add_block(vote_data)

    # Save the updated vote object
    vote.save()

    # Display the generated blockchain code to the user
    blockchain_code = f"ID: {vote.id}\nPrevious Hash: {vote.previous_hash}\nTimestamp: {vote.timestamp}\nData: {vote.data}\nCurrent Hash: {vote.current_hash}\nNonce: {vote.nonce}"
    
    return HttpResponse(f'Vote casted successfully!\n\nGenerated Blockchain Code:\n\n{blockchain_code}')

# views.py

from django.shortcuts import render, get_object_or_404
from .models import Election, Candidate, Vote

def view_results(request):
    # Fetch completed elections
    completed_elections = Election.objects.filter(status='completed')

    # Prepare results for each completed election
    election_results = []
    for election in completed_elections:
        # Fetch candidates for the current election
        candidates = Candidate.objects.filter(election=election)

        # Fetch votes for each candidate
        candidate_results = []
        for candidate in candidates:
            votes_count = Vote.objects.filter(election=election, candidate=candidate).count()
            candidate_results.append({'candidate': candidate, 'votes_count': votes_count})

        # Sort candidate results by votes_count in descending order
        candidate_results.sort(key=lambda x: x['votes_count'], reverse=True)

        election_results.append({'election': election, 'candidates': candidate_results})

    context = {'election_results': election_results}
    return render(request, 'view_results.html', context)
