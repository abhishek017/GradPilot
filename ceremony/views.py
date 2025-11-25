from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from .models import Graduate, StageState
from .forms import SearchForm, CheckInForm, GownForm, StudentDetailForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q


# --------- GRAD ADMIN DASHBOARD --------- #

@login_required
def grad_admin(request):
    stats = Graduate.objects.aggregate(
        total=Count("id"),
        checked_in=Count("id", filter=Q(attended=True)),
        gown_collected=Count("id", filter=Q(gown_collected=True)),
        gown_returned=Count("id", filter=Q(gown_returned=True)),
        total_gown_to_return=Count("id", filter=Q(gown_option__icontains="hire")),
    )

    total = stats["total"]
    checked_in = stats["checked_in"]
    gown_collected = stats["gown_collected"]
    gown_returned = stats["gown_returned"]
    total_gown_to_return = stats["total_gown_to_return"]
    
    graduates = Graduate.objects.all().order_by('unique_id')

    context = {
        'total': total,
        'checked_in': checked_in,
        'gown_collected': gown_collected,
        'gown_returned': gown_returned,
        'total_gown_to_return': total_gown_to_return,
        'graduates': graduates,
    }
    return render(request, 'ceremony/grad_admin.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
def student_detail(request, pk):
    graduate = get_object_or_404(Graduate, pk=pk)

    if request.method == 'POST':
        form = StudentDetailForm(request.POST, request.FILES, instance=graduate)
        if form.is_valid():
            form.save()
            return redirect('grad_admin')
    else:
        form = StudentDetailForm(instance=graduate)

    return render(
        request,
        'ceremony/student_detail.html',
        {'graduate': graduate, 'form': form},
    )


# --------- 1) CHECK-IN / ATTENDANCE --------- #
@login_required
def check_in_search(request):
    form = SearchForm(request.GET or None)
    graduates = []
    all_grads = Graduate.objects.all().order_by('name')

    if form.is_valid() and form.cleaned_data['query']:
        q = form.cleaned_data['query'].strip()
        graduates = Graduate.objects.filter(
            Q(student_id__icontains=q)
            | Q(name__icontains=q)
            | Q(email__icontains=q)
            | Q(unique_id__icontains=q)
            | Q(submission_id__icontains=q)
        ).order_by('name')

    context = {'form': form, 'graduates': graduates, 'all_grads': all_grads}
    return render(request, 'ceremony/check_in_search.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def check_in_detail(request, pk):
    graduate = get_object_or_404(Graduate, pk=pk)

    if request.method == 'POST':
        form = CheckInForm(request.POST, instance=graduate)
        if form.is_valid():
            obj = form.save(commit=False)
            staff_initials = form.cleaned_data.get('staff_initials') or ''
            if obj.attended and not obj.check_in_time:
                obj.mark_attended(staff_initials)
            else:
                obj.save()
            return redirect('check_in_search')
    else:
        form = CheckInForm(instance=graduate)

    return render(
        request,
        'ceremony/check_in_detail.html',
        {'graduate': graduate, 'form': form},
    )


# --------- 2) GOWN DESK --------- #
@login_required
def gown_search(request):
    form = SearchForm(request.GET or None)
    graduates = []
    all_grads = Graduate.objects.all().order_by('name')

    if form.is_valid() and form.cleaned_data['query']:
        q = form.cleaned_data['query'].strip()
        graduates = Graduate.objects.filter(
            Q(student_id__icontains=q)
            | Q(name__icontains=q)
            | Q(email__icontains=q)
            | Q(unique_id__icontains=q)
            | Q(submission_id__icontains=q)
        ).order_by('name')

    context = {'form': form, 'graduates': graduates, 'all_grads': all_grads}
    return render(request, 'ceremony/gown_search.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def gown_detail(request, pk):
    graduate = get_object_or_404(Graduate, pk=pk)

    if request.method == 'POST':
        form = GownForm(request.POST, instance=graduate)
        if form.is_valid():
            form.save()
            return redirect('gown_search')
    else:
        form = GownForm(instance=graduate)

    return render(
        request,
        'ceremony/gown_detail.html',
        {'graduate': graduate, 'form': form},
    )


# --------- 3) STAGE DISPLAY (CONTROL + SCREEN) --------- #

@login_required
def stage_control(request):
    """Back-stage control panel with NEXT button and reordering."""
    state = StageState.get_solo()
    current = state.current_graduate

    def get_attended_queryset():
        return Graduate.objects.filter(
            attended=True,
            gown_collected=True
        ).order_by('unique_id')
    attended_grads = list(get_attended_queryset())

    # def normalize_orders():
    #     """Ensure presentation_order is a dense 1..N sequence for attended grads."""
    #     changed = False
    #     for idx, g in enumerate(attended_grads, start=1):
    #         if g.presentation_order != idx:
    #             g.presentation_order = idx
    #             g.save(update_fields=['presentation_order'])
    #             changed = True
    #     if changed:
    #         # refresh list after normalization
    #         return list(
    #             Graduate.objects.filter(attended=True).order_by('presentation_order', 'name')
    #         )
    #     return attended_grads

    if request.method == 'POST':
        # Reset screen display
        if 'reset' in request.POST:
            state.current_graduate = None
            state.save()
            return redirect('stage_control')

        # Reorder up/down or jump/show from a specific student
        grad_id = request.POST.get('grad_id')
        target = None
        if grad_id:
            try:
                target = Graduate.objects.get(pk=grad_id)
            except Graduate.DoesNotExist:
                target = None

        # # Normalize before any ordering operations
        # attended = normalize_orders()

        if target and target.attended and target.gown_collected:
            # # Move up
            # if 'move_up' in request.POST:
            #     for i, g in enumerate(attended):
            #         if g.pk == target.pk and i > 0:
            #             above = attended[i - 1]
            #             # swap orders
            #             g_order, above_order = g.presentation_order, above.presentation_order
            #             g.presentation_order, above.presentation_order = above_order, g_order
            #             g.save(update_fields=['presentation_order'])
            #             above.save(update_fields=['presentation_order'])
            #             break
            #     return redirect('stage_control')

            # # Move down
            # if 'move_down' in request.POST:
            #     for i, g in enumerate(attended):
            #         if g.pk == target.pk and i < len(attended) - 1:
            #             below = attended[i + 1]
            #             g_order, below_order = g.presentation_order, below.presentation_order
            #             g.presentation_order, below.presentation_order = below_order, g_order
            #             g.save(update_fields=['presentation_order'])
            #             below.save(update_fields=['presentation_order'])
            #             break
            #     return redirect('stage_control')

            # Show on screen / start from here (both behave the same)
            if 'show' in request.POST or 'start_from_here' in request.POST:
                state.current_graduate = target
                state.save()
                return redirect('stage_control')

        # NEXT button
        if 'next' in request.POST:
            # Refresh after possible changes
            attended = list(get_attended_queryset())
            next_grad = None

            if not attended:
                next_grad = None
            elif current and current in attended:
                idx = attended.index(current)
                if idx < len(attended) - 1:
                    next_grad = attended[idx + 1]
                else:
                    next_grad = None  # already at last
            else:
                # No current, or current not in list → start from first
                next_grad = attended[0]

            if next_grad:
                state.current_graduate = next_grad
                state.save()
                current = next_grad

            return redirect('stage_control')
        # For initial GET and after redirects
    attended_grads = get_attended_queryset()

    context = {
        'current': current,
        'attended_grads': attended_grads,
    }
    return render(request, 'ceremony/stage_control.html', context)        

        

@login_required
def stage_display(request):
    """Big screen – read-only view that just shows current graduate."""
    state = StageState.get_solo()
    current = state.current_graduate
    return render(request, 'ceremony/stage_display.html', {'current': current})
