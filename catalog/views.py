from django.shortcuts import render;
from django.views import generic;
from .models import Book, BookInstance, Author, Genre;
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy



# Create your views here.
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    context_object_name = 'book_list'   # your own name for the list as a template variable
    #queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    queryset = Book.objects.all()[:5] # Get 5 books containing the title war
    template_name = 'books/index.html'  # Specify your own template name/location
    paginate_by = 2
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    
    #def get_queryset(self):
     #   return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
     
    #def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
     #   context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
    #    context['some_data'] = 'This is just some data'
     #   return context
     
class BookDetailView(generic.DetailView):
    model = Book
    context_object_name = 'book'   # your own name for the list as a template variable
    template_name = 'books/view.html'  # Specify your own template name/location
 
 #function to retrieve a book-detailed   
#def book_detail_view(request, primary_key):
    #try:
        #book = Book.objects.get(pk=primary_key)
    #except Book.DoesNotExist:
        #raise Http404('Book does not exist')
    
    #or use the below to raise the 404 error page  
    #book = get_object_or_404(Book, pk=primary_key)

    #return render(request, 'catalog/book_detail.html', context={'book': book})
    
class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'author_list'   # your own name for the list as a template variable
    queryset = Author.objects.all()[:5] # Get 5 books containing the title war
    template_name = 'authors/index.html'  # Specify your own template name/location
    paginate_by = 2
    
     
class AuthorDetailView(generic.DetailView):
    model = Author
    context_object_name = 'author'   # your own name for the list as a template variable
    template_name = 'authors/view.html'  # Specify your own template name/location
    
class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='books/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
 
@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)    
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('/') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(LoginRequiredMixin,CreateView):
    model = Author
    template_name ='author_form.html'
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}

class AuthorUpdate(LoginRequiredMixin,UpdateView):
    model = Author
    template_name ='author_form.html'
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(LoginRequiredMixin,DeleteView):
    model = Author
    template_name ='author_confirm_delete.html'
    success_url = reverse_lazy('authors')


